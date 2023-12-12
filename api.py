from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from birdnetlib import Recording
from birdnetlib.analyzer import Analyzer
from datetime import datetime, timedelta
import time
from pydub import AudioSegment, effects

api = Flask(__name__)
api.config.from_pyfile("config.cfg")

CORS(api)

dir_path = os.path.join(api.config['UPLOAD_FOLDER'])

# Load and initialize the BirdNET-Analyzer models.
analyzer = Analyzer()

@api.route("/analyze_api", methods=["POST", "GET"])
def analyze_api():
    if request.method=="GET":
        return "you got me!"

    if 'audio' not in request.files:
        return 'No file part', 400

    audio = request.files['audio']

    save_path = os.path.join(dir_path, audio.filename)
    audio.save(save_path)

    rawsound = AudioSegment.from_file(save_path, "mp3")
    if rawsound.duration_seconds>30:
        os.remove(save_path)
        return 'Audio too long.', 413

    lat = request.form.get("lat")
    lon = request.form.get("lon")

    try:
        lat = float(lat)
        lon = float(lon)
    except Exception as e:
        print(e)
        lat = None
        lon = None

    print(lat, lon)
    print(datetime.utcnow() + timedelta(hours=8))
    
    if lat and lon:
        recording = Recording(
        analyzer,
        save_path,
        lat=lat,
        lon=lon,
        date = datetime.utcnow() + timedelta(hours=8),
        min_conf=0.01,
        sensitivity=1.5,
        )
    else:
        recording = Recording(
        analyzer,
        save_path,
        date = datetime.utcnow() + timedelta(hours=8),
        min_conf=0.01,
        sensitivity=1.5,
        )

    

    
    # rawsound = effects.normalize(rawsound)
    # os.remove(save_path)
    # rawsound.export(save_path, format="mp3")
    # print("sound normalized")

    # Analyze the uploaded recording using birdnetlib
    recording = Recording(
        analyzer,
        save_path,
        min_conf=0.01,
        sensitivity=1.5,
    )
    recording.analyze()
    os.remove(save_path)

    print(recording)
    

    if recording.detections:
        # Return the analysis results to the user
        results = {
            'detections': recording.detections,
        }
        return jsonify(results)
    else:
        results = {
            'detections': "none",
        }
        return jsonify(results)

if __name__=="__main__":
    api.run(debug=True, host="0.0.0.0", port=12345)