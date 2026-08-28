"""Metrics engine for evaluating scheduler performance."""
from typing import List, Tuple, Dict
from models import ScanResult, FrequencyBand
from simulation.environment import RFEnvironment
import numpy as np


class MetricsEngine:
    """Calculates detection, interception, and performance metrics."""

    def __init__(self, reward_config: dict = None):
        self.reward_config = reward_config or {
            "important_detection": 10,
            "normal_detection": 3,
            "miss": -1,
            "false_alarm": -3,
            "scan_delay_per_step": -0.05
        }

    def calculate(self, scan_history: List[ScanResult], environment: RFEnvironment,
                  bands: List[FrequencyBand], time_range: Tuple[float, float]) -> dict:
        if not scan_history:
            return self._empty_metrics()

        total_scans = len(scan_history)
        total_hits = sum(1 for h in scan_history if h.result == 'HIT')
        total_misses = total_scans - total_hits

        # Detection Rate: successful detections / actual emitter activity windows
        actual_opportunities = 0
        successful_detections = 0
        for h in scan_history:
            band = next((b for b in bands if b.id == h.band_id), None)
            if band:
                was_active = environment.is_active(band, h.start_time)
                if was_active:
                    actual_opportunities += 1
                    if h.result == 'HIT':
                        successful_detections += 1

        # Count total activity windows across all bands at all scan times
        total_activity_windows = 0
        for h in scan_history:
            for b in bands:
                if environment.is_active(b, h.start_time):
                    total_activity_windows += 1

        detection_rate = successful_detections / max(1, total_activity_windows)
        interception_rate = successful_detections / max(1, actual_opportunities)

        # Average Intercept Time
        emitter_first_active = {}
        emitter_first_detected = {}
        for h in scan_history:
            for eid in h.detected_emitters:
                if eid not in emitter_first_detected:
                    emitter_first_detected[eid] = h.start_time

        # Track when emitters become active
        step_times = sorted(set(h.start_time for h in scan_history))
        for t in step_times:
            for emitter in environment.get_active_emitters(t):
                if emitter.id not in emitter_first_active:
                    emitter_first_active[emitter.id] = t

        intercept_times = []
        for eid in emitter_first_detected:
            if eid in emitter_first_active:
                delay = emitter_first_detected[eid] - emitter_first_active[eid]
                intercept_times.append(max(0, delay))

        avg_intercept_time = float(np.mean(intercept_times)) if intercept_times else 0.0

        # False Alarm Rate: scans that returned HIT but no emitter was actually active
        false_alarms = 0
        true_detections = 0
        for h in scan_history:
            if h.result == 'HIT':
                band = next((b for b in bands if b.id == h.band_id), None)
                if band and not environment.is_active(band, h.start_time):
                    false_alarms += 1
                else:
                    true_detections += 1

        false_alarm_rate = false_alarms / max(1, total_scans)

        # Reward calculation
        total_reward = 0
        for h in scan_history:
            total_reward += self.reward_config["scan_delay_per_step"]
            if h.result == 'HIT':
                if len(h.detected_emitters) > 1:
                    total_reward += self.reward_config["important_detection"]
                else:
                    total_reward += self.reward_config["normal_detection"]
            else:
                total_reward += self.reward_config["miss"]

        total_reward += false_alarms * self.reward_config["false_alarm"]

        # Prediction accuracy (based on hit rate as proxy)
        prediction_accuracy = total_hits / max(1, total_scans)

        return {
            "detection_rate": round(detection_rate, 4),
            "interception_rate": round(interception_rate, 4),
            "average_intercept_time": round(avg_intercept_time, 4),
            "false_alarm_rate": round(false_alarm_rate, 4),
            "prediction_accuracy": round(prediction_accuracy, 4),
            "total_reward": round(total_reward, 2),
            "total_scans": total_scans,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "unique_emitters_detected": len(emitter_first_detected),
            "total_emitters": len(environment.emitters)
        }

    def _empty_metrics(self) -> dict:
        return {
            "detection_rate": 0.0,
            "interception_rate": 0.0,
            "average_intercept_time": 0.0,
            "false_alarm_rate": 0.0,
            "prediction_accuracy": 0.0,
            "total_reward": 0.0,
            "total_scans": 0,
            "total_hits": 0,
            "total_misses": 0,
            "unique_emitters_detected": 0,
            "total_emitters": 0
        }
