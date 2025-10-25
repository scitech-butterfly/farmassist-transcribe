from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import tempfile
import os

app = Flask(__name__)
# Allow requests only from your frontend URLs
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load the Whisper model once at startup
model = None   # lazy load

@app.route("/api/transcribe", methods=["POST"])
def transcribe():
    global model
    if model is None:
        model = whisper.load_model("tiny")   # smallest model
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]

    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # Transcribe (auto-detect language)
        result = model.transcribe(tmp_path, language=None)
        text = result["text"].strip()
        lang = result.get("language", "unknown")
        return jsonify({"text": text, "language": lang})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)




