"""
metrics_evaluator.py
---------------------
Computes the electronic-support figures of merit called out in the
problem statement:

  Probability of Detection (P_int) = Intercepted Pulses / Total Transmitted Pulses
  False Alarm Rate        (P_fa)  = False Interceptions / Total Sweep Windows
  Average Intercept Time Error    = mean(|predicted_activity_time - actual_detection_time|)

Also exposes a convenience wrapper that takes raw predicted-vs-actual
emitter-id lists (as produced by pulse_classifier.evaluate_accuracy) and
derives P_int / P_fa / time-error from them.
"""

import numpy as np


def probability_of_detection(intercepted_pulses, total_transmitted_pulses):
    """P_int = Intercepted Pulses / Total Transmitted Pulses"""
    if total_transmitted_pulses == 0:
        return 0.0
    return intercepted_pulses / total_transmitted_pulses


def false_alarm_rate(false_interceptions, total_sweep_windows):
    """P_fa = False Interceptions / Total Sweep Windows"""
    if total_sweep_windows == 0:
        return 0.0
    return false_interceptions / total_sweep_windows


def average_intercept_time_error(predicted_times, actual_times):
    """
    Mean absolute difference between predicted emitter-activity time and
    actual detection time (both array-likes, same length, same units).
    """
    predicted_times = np.asarray(predicted_times, dtype=float)
    actual_times = np.asarray(actual_times, dtype=float)

    if len(predicted_times) != len(actual_times):
        raise ValueError("predicted_times and actual_times must be the same length")
    if len(predicted_times) == 0:
        return 0.0

    return float(np.mean(np.abs(predicted_times - actual_times)))


def evaluate_from_predictions(predicted_labels, actual_labels,
                               total_sweep_windows=None,
                               predicted_times=None, actual_times=None):
    """
    Convenience wrapper: derives P_int / P_fa (+ optional time error) directly
    from predicted vs. actual emitter-id lists, e.g. straight out of
    pulse_classifier.evaluate_accuracy().

    - Intercepted Pulses  : predictions that correctly match a real emitter (non-background) hit
    - False Interceptions : predictions flagged as a detection where the actual label disagrees
    - total_sweep_windows : if not given, defaults to len(actual_labels)
    """
    predicted_labels = np.asarray(predicted_labels)
    actual_labels = np.asarray(actual_labels)

    if len(predicted_labels) != len(actual_labels):
        raise ValueError("predicted_labels and actual_labels must be the same length")

    total_transmitted_pulses = len(actual_labels)
    if total_sweep_windows is None:
        total_sweep_windows = total_transmitted_pulses

    correct_mask = predicted_labels == actual_labels
    intercepted_pulses = int(correct_mask.sum())
    false_interceptions = int((~correct_mask).sum())

    p_int = probability_of_detection(intercepted_pulses, total_transmitted_pulses)
    p_fa = false_alarm_rate(false_interceptions, total_sweep_windows)

    result = {
        "probability_of_detection": round(p_int, 4),
        "false_alarm_rate": round(p_fa, 4),
        "intercepted_pulses": intercepted_pulses,
        "false_interceptions": false_interceptions,
        "total_transmitted_pulses": total_transmitted_pulses,
        "total_sweep_windows": total_sweep_windows,
        "average_intercept_time_error": None,
    }

    if predicted_times is not None and actual_times is not None:
        result["average_intercept_time_error"] = round(
            average_intercept_time_error(predicted_times, actual_times), 4
        )

    return result


if __name__ == "__main__":
    # smoke test with mock predicted/actual labels + timing arrays
    rng = np.random.default_rng(0)

    actual = rng.integers(0, 5, size=200)
    predicted = actual.copy()
    flip_idx = rng.choice(200, size=30, replace=False)
    predicted[flip_idx] = rng.integers(0, 5, size=30)

    actual_times = rng.uniform(0, 100, size=200)
    predicted_times = actual_times + rng.normal(0, 2.0, size=200)

    metrics = evaluate_from_predictions(
        predicted, actual,
        total_sweep_windows=250,
        predicted_times=predicted_times,
        actual_times=actual_times,
    )

    for k, v in metrics.items():
        print(f"{k}: {v}")
