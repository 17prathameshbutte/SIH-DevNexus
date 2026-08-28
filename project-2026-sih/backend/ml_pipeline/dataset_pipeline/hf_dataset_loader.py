"""
hf_dataset_loader.py
---------------------
Downloads and parses alan-turing-institute/turing-synthetic-radar-dataset
from Hugging Face, extracting Pulse Descriptor Words (PDWs):
    Time of Arrival (ToA), Center Frequency, Pulse Width, Angle of Arrival, Amplitude

NOTE ON ACCESS: this dataset is gated on Hugging Face (you must log in and
accept the dataset conditions on the dataset page before it will download).
You'll need:
    pip install datasets huggingface_hub
    huggingface-cli login          # paste a token with read access
      -- or --
    export HF_TOKEN=hf_xxx         # then this script picks it up automatically

Because the exact PDW column names can vary slightly by dataset config/split
(the dataset ships "scan" and "stare" receiver-mode subsets, per the
Turing Synthetic Radar Dataset paper), this loader normalizes whatever raw
column names it finds into the canonical PDW_COLUMNS below. Adjust
COLUMN_ALIASES if the schema you pull down differs from what's mapped here.
"""

import os
import pandas as pd

DATASET_ID = "alan-turing-institute/turing-synthetic-radar-dataset"

PDW_COLUMNS = ["ToA", "Center_Frequency", "Pulse_Width", "AoA", "Amplitude"]

# Map common alternate names -> canonical PDW column name.
# Extend this if the live schema uses different labels.
COLUMN_ALIASES = {
    "toa": "ToA", "time_of_arrival": "ToA", "t_arrival": "ToA",
    "center_frequency": "Center_Frequency", "cf": "Center_Frequency",
    "frequency": "Center_Frequency", "fc": "Center_Frequency",
    "pulse_width": "Pulse_Width", "pw": "Pulse_Width",
    "angle_of_arrival": "AoA", "aoa": "AoA",
    "amplitude": "Amplitude", "power": "Amplitude", "amp": "Amplitude",
    "emitter_id": "emitter_id", "label": "emitter_id", "mode": "receiver_mode",
}


def _normalize_columns(df):
    rename_map = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def load_turing_radar_dataset(config=None, split="train", streaming=False):
    """
    Loads the dataset via the `datasets` library.

    config   : optional dataset config name (e.g. "scan" or "stare" receiver mode,
               check dataset viewer on HF for exact config names)
    split    : "train" | "validation" | "test"
    streaming: True to stream (recommended given dataset size) instead of
               downloading the full split up front.

    Returns a HF `Dataset` (or `IterableDataset` if streaming=True).
    """
    from datasets import load_dataset

    token = os.environ.get("HF_TOKEN")  # None is fine if you've already `huggingface-cli login`

    kwargs = {"split": split, "streaming": streaming}
    if token:
        kwargs["token"] = token
    if config:
        kwargs["name"] = config

    ds = load_dataset(DATASET_ID, **kwargs)
    return ds


def parse_pdws_to_dataframe(hf_dataset, max_rows=None):
    """
    Converts a HF Dataset (or a slice of an IterableDataset) of pulse-train
    records into a flat pandas DataFrame of individual PDWs, normalizing
    column names via COLUMN_ALIASES.

    Handles two common shapes:
      (a) one row per PDW already (flat schema)
      (b) one row per pulse train, with a nested list/column of pulses
          (in which case we explode it)
    """
    rows = []
    for i, record in enumerate(hf_dataset):
        if max_rows is not None and i >= max_rows:
            break

        if "pulses" in record and isinstance(record["pulses"], (list, dict)):
            # nested pulse-train shape -> explode into individual PDW rows
            pulses = record["pulses"]
            if isinstance(pulses, dict):
                # dict-of-lists (columnar) nested structure
                n = len(next(iter(pulses.values())))
                for j in range(n):
                    rows.append({k: v[j] for k, v in pulses.items()})
            else:
                rows.extend(pulses)
        else:
            # already flat: one PDW per record
            rows.append(record)

    df = pd.DataFrame(rows)
    df = _normalize_columns(df)

    # keep only recognized PDW + label-ish columns that are actually present
    keep_cols = [c for c in PDW_COLUMNS + ["emitter_id", "receiver_mode"] if c in df.columns]
    df = df[keep_cols] if keep_cols else df

    return df


def load_and_parse(config=None, split="train", max_rows=5000, streaming=True):
    """Convenience: load + parse in one call."""
    ds = load_turing_radar_dataset(config=config, split=split, streaming=streaming)
    df = parse_pdws_to_dataframe(ds, max_rows=max_rows)
    return df


if __name__ == "__main__":
    try:
        df = load_and_parse(split="train", max_rows=2000, streaming=True)
        print("Parsed PDW dataframe shape:", df.shape)
        print(df.head())
        df.to_csv("test_pdw_sample.csv", index=False)
        print("Saved sample to test_pdw_sample.csv")
    except Exception as e:
        print("Could not download from Hugging Face in this environment:", e)
        print("Falling back to a synthetic PDW sample so downstream scripts "
              "(pulse_classifier.py, metrics_evaluator.py) can still be smoke-tested.")
        import sys
        sys.path.append("../ml_engine")
        from mock_rf_feed import generate_pdw_batch
        import numpy as np

        raw = generate_pdw_batch(n_samples=500, seed=99)
        toa = np.cumsum(np.random.uniform(0.5, 5.0, size=500))  # simulated arrival times (us)
        emitter_id = np.random.randint(0, 5, size=500)          # 5 mock emitter classes

        df = pd.DataFrame(raw, columns=["Center_Frequency", "Pulse_Width", "Amplitude", "AoA"])
        df.insert(0, "ToA", toa)
        df["emitter_id"] = emitter_id

        df.to_csv("test_pdw_sample.csv", index=False)
        print("Saved synthetic fallback sample to test_pdw_sample.csv:", df.shape)
