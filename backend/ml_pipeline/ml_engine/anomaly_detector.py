"""
anomaly_detector.py
--------------------
Unknown-threat / uncatalogued-emitter detector.

Uses sklearn's DBSCAN (same density-based clustering pattern practiced in
DBSCAN.ipynb) to cluster scaled PDW features. Any point DBSCAN assigns to
label == -1 is flagged as a "noise" point -> in this context, an
uncatalogued / frequency-hopping signal that doesn't match any known
emitter cluster.

Also implements automatic epsilon selection via a k-NN distance graph
(the classic "elbow of the k-distance plot" heuristic), so eps=0.3 is
used as a sane default but can be re-estimated from the data itself.
"""

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

DEFAULT_EPS = 0.3
DEFAULT_MIN_SAMPLES = 5


def estimate_optimal_eps(X, min_samples=DEFAULT_MIN_SAMPLES):
    """
    Computes the k-NN distance graph (k = min_samples) and returns the
    'knee' distance as a candidate epsilon, using the same rise-in-sorted-
    distance heuristic behind the elbow method used for KMeans in
    KMeans.ipynb, applied here to the k-distance curve instead of WCSS.
    """
    neighbors = NearestNeighbors(n_neighbors=min_samples)
    neighbors_fit = neighbors.fit(X)
    distances, _ = neighbors_fit.kneighbors(X)

    # distance to the k-th nearest neighbor, sorted ascending
    k_distances = np.sort(distances[:, -1])

    # simple knee heuristic: point of maximum curvature via second derivative
    if len(k_distances) < 3:
        return DEFAULT_EPS

    first_deriv = np.diff(k_distances)
    second_deriv = np.diff(first_deriv)
    knee_index = int(np.argmax(second_deriv)) + 2  # offset for double diff
    knee_index = min(knee_index, len(k_distances) - 1)

    optimal_eps = float(k_distances[knee_index])
    return optimal_eps if optimal_eps > 0 else DEFAULT_EPS


def fit_anomaly_engine(X_scaled, eps=None, min_samples=DEFAULT_MIN_SAMPLES,
                        auto_eps=False):
    """
    X_scaled   : (N, D) scaled feature matrix (output of preprocessing.scale_pdw_features)
    eps        : DBSCAN neighborhood radius; if None and auto_eps=True, will be estimated
    min_samples: DBSCAN core-point threshold
    auto_eps   : if True, ignore `eps` and compute it via estimate_optimal_eps()

    Returns (labels, dbscan_model, eps_used)
        labels : (N,) array; -1 marks flagged/uncatalogued signals
    """
    if auto_eps or eps is None:
        eps = estimate_optimal_eps(X_scaled, min_samples=min_samples)

    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)

    return labels, dbscan, eps


def flag_uncatalogued(labels):
    """Boolean mask: True where a sample is flagged as an unknown/new emitter (-1)."""
    return labels == -1


def summarize_flags(labels):
    total = len(labels)
    n_flagged = int(np.sum(labels == -1))
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    return {
        "total_samples": total,
        "num_known_clusters": n_clusters,
        "num_flagged_unknown": n_flagged,
        "flagged_ratio": round(n_flagged / total, 4) if total else 0.0,
    }


if __name__ == "__main__":
    from mock_rf_feed import generate_pdw_batch
    from preprocessing import scale_pdw_features

    raw = generate_pdw_batch(n_samples=200, seed=7)
    X_scaled, _ = scale_pdw_features(raw, fit=True)

    labels, model, eps_used = fit_anomaly_engine(X_scaled, auto_eps=True,
                                                   min_samples=DEFAULT_MIN_SAMPLES)
    print("eps used:", eps_used)
    print(summarize_flags(labels))
