import pickle
from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F
from flask import Flask, jsonify, render_template, request

from dataset_preprocessing import build_feature_matrix
from pulse_classifier import PulseClassifier


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "pulse_classifier.pkl"

app = Flask(__name__)
_model_bundle = None


def load_model_bundle():
    global _model_bundle
    if _model_bundle is None:
        with MODEL_PATH.open("rb") as model_file:
            bundle = pickle.load(model_file)

        architecture = bundle["architecture"]
        model = PulseClassifier(**architecture)
        model.load_state_dict(bundle["state_dict"])
        model.eval()
        _model_bundle = (model, bundle["scaler"], bundle["vectorizer"])

    return _model_bundle


def predict_emitter(values):
    model, scaler, vectorizer = load_model_bundle()
    raw_row = pd.DataFrame([values])
    features, _, _, _, _ = build_feature_matrix(
        raw_row, fit=False, scaler=scaler, vectorizer=vectorizer
    )

    with torch.no_grad():
        scores = model(torch.tensor(features, dtype=torch.float32))
        probabilities = F.softmax(scores, dim=1)
        confidence, predicted_class = torch.max(probabilities, dim=1)

    return {
        "emitter_class": int(predicted_class.item()),
        "confidence": round(float(confidence.item()), 4),
    }


def read_values(source):
    required_fields = [
        "ToA",
        "Center_Frequency",
        "Pulse_Width",
        "AoA",
        "Amplitude",
        "receiver_mode",
    ]
    values = {}
    for field in required_fields:
        raw_value = source.get(field, "")
        if raw_value is None or str(raw_value).strip() == "":
            raise ValueError(f"{field.replace('_', ' ')} is required.")
        values[field] = (
            str(raw_value).strip()
            if field == "receiver_mode"
            else float(raw_value)
        )
    return values


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    form_values = request.form.to_dict()

    if request.method == "POST":
        try:
            result = predict_emitter(read_values(request.form))
        except (ValueError, KeyError, FileNotFoundError, RuntimeError) as exc:
            error = str(exc)

    return render_template("index.html", result=result, error=error, form=form_values)


@app.post("/api/predict")
def api_predict():
    try:
        payload = request.get_json(silent=True) or {}
        return jsonify(predict_emitter(read_values(payload)))
    except (ValueError, KeyError, FileNotFoundError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)