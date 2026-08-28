"""
export_pkl.py
--------------
Exports the trained SmartScanScheduler as a .pkl file (requested format).

Note: PyTorch's native .pth/.pt files ARE pickle files under the hood
(torch.save uses Python's pickle protocol). This script just repackages
the trained weights + the minimal metadata needed to reconstruct the model
into a plain .pkl using Python's pickle module directly, so it opens with
a standard `pickle.load()` without requiring torch.load specifically.
"""

import pickle
import torch

from model import SmartScanScheduler
from mock_rf_feed import NUM_CHANNELS, NUM_TIMESTEPS

PTH_PATH = "smart_scan_v1.pth"
PKL_PATH = "smart_scan_v1.pkl"

INPUT_DIM = NUM_CHANNELS * NUM_TIMESTEPS
NUM_BANDS = NUM_CHANNELS


def export_to_pkl(pth_path=PTH_PATH, pkl_path=PKL_PATH):
    model = SmartScanScheduler(input_dim=INPUT_DIM, num_bands=NUM_BANDS)
    state_dict = torch.load(pth_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    # bundle state_dict + architecture metadata so the model can be
    # reconstructed on load without needing the .pth file around
    bundle = {
        "state_dict": model.state_dict(),
        "architecture": {
            "input_dim": INPUT_DIM,
            "num_bands": NUM_BANDS,
            "hidden_dims": (128, 64),
        },
        "model_class": "SmartScanScheduler",
    }

    with open(pkl_path, "wb") as f:
        pickle.dump(bundle, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Exported {pkl_path}")
    return pkl_path


def load_from_pkl(pkl_path=PKL_PATH):
    """Reference loader: reconstructs the model from the .pkl bundle."""
    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)

    arch = bundle["architecture"]
    model = SmartScanScheduler(
        input_dim=arch["input_dim"],
        num_bands=arch["num_bands"],
        hidden_dims=arch["hidden_dims"],
    )
    model.load_state_dict(bundle["state_dict"])
    model.eval()
    return model


if __name__ == "__main__":
    export_to_pkl()

    # round-trip sanity check
    reloaded_model = load_from_pkl()
    dummy = torch.randn(1, INPUT_DIM)
    dwell, band_logits = reloaded_model(dummy)
    print("Round-trip check OK -> dwell shape:", dwell.shape, "band_logits shape:", band_logits.shape)
