"""
preprocessing.py
-----------------
1) Feature scaling: normalizes raw RF variables (fc, PW, Amplitude, AoA)
   into zero-mean, unit-variance matrices using sklearn's StandardScaler
   (same pattern used in ANN_Regression.ipynb / ANN_Classification.ipynb).

2) Sanitization: cleans diagnostic error logs using Regex + NLTK, following
   the same lower-case / strip-punctuation / stopword-removal pipeline
   built up in REGEX.ipynb.
"""

import re
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ---------------------------------------------------------------------------
# NLTK setup (idempotent — safe to call every run)
# ---------------------------------------------------------------------------
def _ensure_nltk_resources():
    for resource in ("punkt", "punkt_tab", "stopwords"):
        try:
            nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource
                            else f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)


# ---------------------------------------------------------------------------
# 1. Feature scaling
# ---------------------------------------------------------------------------
PDW_COLUMNS = ["Center_Frequency", "Pulse_Width", "Amplitude", "AoA"]


def scale_pdw_features(raw_pdw, scaler=None, fit=True):
    """
    raw_pdw : array-like (N, 4) -> [fc, PW, Amplitude, AoA]
    scaler  : an existing fitted StandardScaler to reuse (e.g. at inference),
              or None to fit a new one.
    fit     : if True, fit_transform; if False, transform only (inference).

    Returns (scaled_matrix, scaler) so the caller can persist the scaler
    for later inference (mirrors X_train_scaled / X_test_scaled pattern).
    """
    df = pd.DataFrame(raw_pdw, columns=PDW_COLUMNS)

    if scaler is None:
        scaler = StandardScaler()

    if fit:
        scaled = scaler.fit_transform(df)
    else:
        scaled = scaler.transform(df)

    return scaled, scaler


# ---------------------------------------------------------------------------
# 2. Diagnostic log sanitization (Regex + NLTK)
# ---------------------------------------------------------------------------
def _remove_urls(text):
    return re.sub(r"http\S+", "", text)


def _remove_punc(text):
    if pd.isna(text):
        return ""
    return re.sub(r"[^A-Za-z0-9\s]", "", text)


def _remove_non_ascii_tags(text):
    return re.sub(r"[<>*?]", "", text)


def _remove_stopwords(text):
    _ensure_nltk_resources()
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    cleaned_tokens = [tok for tok in tokens if tok.lower() not in stop_words]
    return " ".join(cleaned_tokens)


def sanitize_log_line(text):
    """Apply the full cleaning chain to a single diagnostic log line."""
    text = text.lower()
    text = _remove_urls(text)
    text = _remove_non_ascii_tags(text)
    text = _remove_punc(text)
    text = _remove_stopwords(text)
    return text.strip()


def sanitize_log_series(log_series):
    """
    log_series : pandas Series of raw diagnostic log strings
    returns    : pandas Series of cleaned log strings
    """
    _ensure_nltk_resources()
    return log_series.astype(str).apply(sanitize_log_line)


if __name__ == "__main__":
    from mock_rf_feed import generate_pdw_batch

    # --- demo: scale mock PDW features ---
    raw = generate_pdw_batch(n_samples=8, seed=1)
    scaled, fitted_scaler = scale_pdw_features(raw, fit=True)
    print("Raw PDW sample:\n", raw[:3])
    print("\nScaled PDW sample (zero-mean, unit-var):\n", scaled[:3])

    # --- demo: sanitize mock diagnostic logs ---
    mock_logs = pd.Series([
        "ERROR!! Receiver <lock> lost @ freq=12000MHz see http://logs.local/1234",
        "WARNING: AoA estimate unstable, retrying scan..."
    ])
    cleaned = sanitize_log_series(mock_logs)
    print("\nCleaned diagnostic logs:\n", cleaned.tolist())
