"""
dataset_preprocessing.py
-------------------------
Formats parsed PDW sequences into a clean pandas DataFrame, then:
  - applies TfidfVectorizer to categorical radar mode tags
  - normalizes numerical PDW channels (ToA, Center_Frequency, Pulse_Width,
    AoA, Amplitude) with StandardScaler

Follows the same StandardScaler pattern used across ANN_Regression.ipynb /
ANN_Classification.ipynb, and the TfidfVectorizer pattern from REGEX.ipynb.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

NUMERIC_PDW_COLS = ["ToA", "Center_Frequency", "Pulse_Width", "AoA", "Amplitude"]
MODE_TAG_COL = "receiver_mode"   # categorical radar mode tag, e.g. "scan" / "stare"


def build_clean_dataframe(raw_df):
    """
    Coerces numeric PDW columns to float, drops fully-empty rows, and
    fills a default mode tag if the column isn't present.
    """
    df = raw_df.copy()

    for col in NUMERIC_PDW_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if MODE_TAG_COL not in df.columns:
        df[MODE_TAG_COL] = "unknown_mode"
    df[MODE_TAG_COL] = df[MODE_TAG_COL].astype(str).str.lower().str.strip()

    df = df.dropna(subset=[c for c in NUMERIC_PDW_COLS if c in df.columns], how="all")
    df = df.reset_index(drop=True)

    return df


def tfidf_encode_mode_tags(df, vectorizer=None, fit=True, max_features=50):
    """
    Applies TfidfVectorizer to the categorical radar-mode tag column
    (treats each tag string as a mini "document").
    Returns (tfidf_matrix, vectorizer).
    """
    if vectorizer is None:
        vectorizer = TfidfVectorizer(max_features=max_features)

    tags = df[MODE_TAG_COL].fillna("unknown_mode")

    if fit:
        tfidf_matrix = vectorizer.fit_transform(tags)
    else:
        tfidf_matrix = vectorizer.transform(tags)

    return tfidf_matrix, vectorizer


def scale_numeric_pdw(df, scaler=None, fit=True):
    """
    StandardScaler over the numeric PDW columns present in df.
    Returns (scaled_matrix, scaler, used_columns).
    """
    used_cols = [c for c in NUMERIC_PDW_COLS if c in df.columns]
    numeric_df = df[used_cols].fillna(df[used_cols].median(numeric_only=True))

    if scaler is None:
        scaler = StandardScaler()

    if fit:
        scaled = scaler.fit_transform(numeric_df)
    else:
        scaled = scaler.transform(numeric_df)

    return scaled, scaler, used_cols


def build_feature_matrix(raw_df, fit=True, scaler=None, vectorizer=None):
    """
    End-to-end: clean -> scale numeric PDWs -> TF-IDF the mode tag -> concat.
    Returns (X, y, scaler, vectorizer, feature_names)
        y is the 'emitter_id' label column if present, else None.
    """
    df = build_clean_dataframe(raw_df)

    scaled_numeric, scaler, used_cols = scale_numeric_pdw(df, scaler=scaler, fit=fit)
    tfidf_matrix, vectorizer = tfidf_encode_mode_tags(df, vectorizer=vectorizer, fit=fit)

    X = np.hstack([scaled_numeric, tfidf_matrix.toarray()])

    y = df["emitter_id"].values if "emitter_id" in df.columns else None

    feature_names = used_cols + [f"tag_tfidf_{t}" for t in vectorizer.get_feature_names_out()]

    return X, y, scaler, vectorizer, feature_names


if __name__ == "__main__":
    # quick smoke test against test_pdw_sample.csv produced by hf_dataset_loader.py
    df = pd.read_csv("test_pdw_sample.csv")
    X, y, scaler, vectorizer, feature_names = build_feature_matrix(df, fit=True)

    print("Feature matrix shape:", X.shape)
    print("Num features:", len(feature_names))
    print("Labels present:", y is not None)
