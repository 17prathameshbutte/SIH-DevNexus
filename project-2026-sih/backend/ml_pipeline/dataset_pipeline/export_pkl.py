"""
export_pkl.py
--------------
Exports the trained PulseClassifier as a .pkl file (requested format).
See ml_engine/export_pkl.py for the equivalent on the scheduler model.
"""

import pickle
import torch

from pulse_classifier import PulseClassifier, prepare_tensors

PTH_PATH = "pulse_classifier.pth"
PKL_PATH = "pulse_classifier.pkl"


def export_to_pkl(csv_path="test_pdw_sample.csv", pth_path=PTH_PATH, pkl_path=PKL_PATH):
    # re-derive input_dim/num_classes the same way training did
    X_train_t, y_train_t, X_test_t, y_test_t, scaler, vectorizer, feature_names = \
        prepare_tensors(csv_path)

    num_classes = int(torch.cat([y_train_t, y_test_t]).max().item()) + 1
    input_dim = X_train_t.shape[1]

    model = PulseClassifier(input_dim=input_dim, num_classes=num_classes)
    state_dict = torch.load(pth_path, map_location="cpu")
    model.load_state_dict(state_dict)
    model.eval()

    bundle = {
        "state_dict": model.state_dict(),
        "architecture": {"input_dim": input_dim, "num_classes": num_classes},
        "model_class": "PulseClassifier",
        "scaler": scaler,          # fitted StandardScaler, for inference reuse
        "vectorizer": vectorizer,  # fitted TfidfVectorizer, for inference reuse
        "feature_names": feature_names,
    }

    with open(pkl_path, "wb") as f:
        pickle.dump(bundle, f, protocol=pickle.HIGHEST_PROTOCOL)

    print(f"Exported {pkl_path}")
    return pkl_path


def load_from_pkl(pkl_path=PKL_PATH):
    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)

    arch = bundle["architecture"]
    model = PulseClassifier(input_dim=arch["input_dim"], num_classes=arch["num_classes"])
    model.load_state_dict(bundle["state_dict"])
    model.eval()
    return model, bundle["scaler"], bundle["vectorizer"], bundle["feature_names"]


if __name__ == "__main__":
    export_to_pkl()

    reloaded_model, scaler, vectorizer, feature_names = load_from_pkl()
    dummy = torch.randn(1, reloaded_model.model[0].in_features)
    out = reloaded_model(dummy)
    print("Round-trip check OK -> output shape:", out.shape)
