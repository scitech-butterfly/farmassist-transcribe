from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import tempfile
import os
from pydub import AudioSegment

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    "https://farmassist-frontend.onrender.com"
]}})

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Save the MP3 temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        audio_file.save(tmp.name)
        mp3_path = tmp.name

    wav_path = mp3_path.replace(".mp3", ".wav")

    try:
        # Convert MP3 → WAV (Google Speech only supports wav/flac/aiff)
        AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        # 🔹 Try English first
        try:
            text = recognizer.recognize_google(audio_data, language="en-IN")
            detected_lang = "en"
        except sr.UnknownValueError:
            # 🔹 Retry with Hindi
            text = recognizer.recognize_google(audio_data, language="hi-IN")
            detected_lang = "hi"

        return jsonify({"text": text, "language": detected_lang})

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(mp3_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
