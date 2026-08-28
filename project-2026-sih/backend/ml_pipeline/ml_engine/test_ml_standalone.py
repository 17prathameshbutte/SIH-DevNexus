"""
test_ml_standalone.py
----------------------
Independent smoke test: loads (or generates) mock input JSONs, calls
predict_step(), and prints the resulting JSON contract. Requires no
external services — everything is simulated locally via mock_rf_feed.py.

Run:
    python test_ml_standalone.py
"""

import json
import numpy as np

from mock_rf_feed import NUM_CHANNELS, NUM_TIMESTEPS, generate_pdw_batch
from api_wrapper import predict_step

MOCK_INPUT_PATH = "mock_input.json"


def build_mock_input_json(path=MOCK_INPUT_PATH, seed=123):
    rng = np.random.default_rng(seed)

    occupancy_matrix = rng.normal(loc=-80, scale=10,
                                   size=(NUM_CHANNELS, NUM_TIMESTEPS)).tolist()
    pdw_batch = generate_pdw_batch(n_samples=25, seed=seed).tolist()

    payload = {
        "occupancy_matrix": occupancy_matrix,
        "pdw_batch": pdw_batch,
    }

    with open(path, "w") as f:
        json.dump(payload, f, indent=2)

    return payload


def run_standalone_test():
    print("Building mock input JSON ...")
    payload = build_mock_input_json()

    print(f"Loading mock input from {MOCK_INPUT_PATH} ...")
    with open(MOCK_INPUT_PATH, "r") as f:
        loaded_payload = json.load(f)

    print("Calling predict_step() ...\n")
    output = predict_step(loaded_payload)

    print("=== predict_step() output ===")
    print(json.dumps(output, indent=2))

    assert output["status"] == "ok", f"predict_step failed: {output.get('error')}"
    print("\nSmoke test PASSED.")


if __name__ == "__main__":
    run_standalone_test()
