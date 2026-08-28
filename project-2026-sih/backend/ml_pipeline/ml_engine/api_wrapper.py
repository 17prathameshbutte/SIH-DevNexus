"""
api_wrapper.py
--------------
Wraps SmartScanScheduler + the DBSCAN anomaly engine behind a single
predict_step(input_json) function returning a defined JSON contract, so
the ml_engine/ module can be dropped behind any REST/RPC layer untouched.

Expected input_json:
{
    "occupancy_matrix": [[...], [...], ...],   # (C, T) = (10, 50) floats
    "pdw_batch": [[fc, PW, Amplitude, AoA], ...]   # optional, (N, 4) floats
}

Returned JSON contract:
{
    "predicted_dwell_time_ms": float,
    "next_sweep_band_index": int,
    "band_confidence": float,
    "anomaly_flags": [bool, ...] | null,
    "num_uncatalogued_signals": int | null,
    "status": "ok" | "error",
    "error": str | null
}
"""

import json
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

import pickle

try:
    from .model import SmartScanScheduler
    from .mock_rf_feed import NUM_CHANNELS, NUM_TIMESTEPS
    from .preprocessing import scale_pdw_features
    from .anomaly_detector import fit_anomaly_engine, flag_uncatalogued
except ImportError:
    from model import SmartScanScheduler
    from mock_rf_feed import NUM_CHANNELS, NUM_TIMESTEPS
    from preprocessing import scale_pdw_features
    from anomaly_detector import fit_anomaly_engine, flag_uncatalogued

PIPELINE_DIR = Path(__file__).resolve().parent
PKL_PATH = PIPELINE_DIR / "smart_scan_v1.pkl"
PTH_PATH = PIPELINE_DIR / "smart_scan_v1.pth"
INPUT_DIM = NUM_CHANNELS * NUM_TIMESTEPS
NUM_BANDS = NUM_CHANNELS

_model_cache = {"model": None}


def _load_model():
    if _model_cache["model"] is not None:
        return _model_cache["model"]

    # preferred: load from the .pkl bundle (state_dict + architecture)
    try:
        with open(PKL_PATH, "rb") as f:
            bundle = pickle.load(f)
        arch = bundle["architecture"]
        model = SmartScanScheduler(
            input_dim=arch["input_dim"],
            num_bands=arch["num_bands"],
            hidden_dims=arch.get("hidden_dims", (128, 64)),
        )
        model.load_state_dict(bundle["state_dict"])
        model.eval()
        _model_cache["model"] = model
        return model
    except FileNotFoundError:
        pass

    # fallback: .pth weights (run export_pkl.py to produce the .pkl)
    model = SmartScanScheduler(input_dim=INPUT_DIM, num_bands=NUM_BANDS)
    try:
        state_dict = torch.load(PTH_PATH, map_location="cpu")
        model.load_state_dict(state_dict)
    except FileNotFoundError:
        # untrained weights so the API stays functional for smoke-testing
        pass
    model.eval()
    _model_cache["model"] = model
    return model


def predict_step(input_json):
    """
    input_json : dict or JSON string matching the contract in the module docstring.
    Returns a dict matching the output contract (also JSON-serializable).
    """
    try:
        if isinstance(input_json, str):
            input_json = json.loads(input_json)

        occupancy_matrix = np.array(input_json["occupancy_matrix"], dtype=np.float32)
        if occupancy_matrix.shape != (NUM_CHANNELS, NUM_TIMESTEPS):
            raise ValueError(
                f"occupancy_matrix must be shape ({NUM_CHANNELS}, {NUM_TIMESTEPS}), "
                f"got {occupancy_matrix.shape}"
            )

        model = _load_model()
        x = torch.tensor(occupancy_matrix.flatten(), dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            dwell_pred, band_logits = model(x)
            band_probs = F.softmax(band_logits, dim=1)
            band_idx = int(torch.argmax(band_probs, dim=1).item())
            band_conf = float(band_probs[0, band_idx].item())

        result = {
            "predicted_dwell_time_ms": round(float(dwell_pred.item()), 4),
            "next_sweep_band_index": band_idx,
            "band_confidence": round(band_conf, 4),
            "anomaly_flags": None,
            "num_uncatalogued_signals": None,
            "status": "ok",
            "error": None,
        }

        # optional: run anomaly engine if a PDW batch was supplied
        if "pdw_batch" in input_json and input_json["pdw_batch"]:
            raw_pdw = np.array(input_json["pdw_batch"], dtype=np.float32)
            X_scaled, _ = scale_pdw_features(raw_pdw, fit=True)
            labels, _, _ = fit_anomaly_engine(X_scaled, auto_eps=True)
            flags = flag_uncatalogued(labels)

            result["anomaly_flags"] = flags.tolist()
            result["num_uncatalogued_signals"] = int(flags.sum())

        return result

    except Exception as e:
        return {
            "predicted_dwell_time_ms": None,
            "next_sweep_band_index": None,
            "band_confidence": None,
            "anomaly_flags": None,
            "num_uncatalogued_signals": None,
            "status": "error",
            "error": str(e),
        }


if __name__ == "__main__":
    mock_input = {
        "occupancy_matrix": np.random.randn(NUM_CHANNELS, NUM_TIMESTEPS).tolist(),
        "pdw_batch": np.random.uniform(low=[2000, 0.1, -90, 0],
                                        high=[18000, 50, -10, 360],
                                        size=(20, 4)).tolist(),
    }
    output = predict_step(mock_input)
    print(json.dumps(output, indent=2))
