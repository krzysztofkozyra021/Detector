from flask import Flask, request, jsonify, render_template
import cv2
import numpy as np
from detector import detect_signs
from model import load_trained_model

app = Flask(__name__)
model = load_trained_model("polskie_znaki_model_92.pth")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "Brak pliku w żądaniu"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Nie wybrano pliku"}), 400
    if not file.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        return jsonify(
            {"error": "Niepoprawny format pliku. Obsługiwane są tylko PNG, JPG i WebP."}
        ), 400
    try:
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Nie można zdekodować obrazu"}), 400
        if model is None:
            return jsonify(
                {"error": "Model nie jest załadowany. Najpierw wytrenuj model."}
            ), 500
        predictions = detect_signs(img, model)
        response = {
            "sign_detected": len(predictions) > 0,
            "count": len(predictions),
            "predictions": predictions,
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
