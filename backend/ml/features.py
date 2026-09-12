"""Feature engineering for SmartScan-EW scheduler.

IMPORTANT: All features use ONLY historical information available up to the current time.
NO future data is ever used. This is enforced by only looking at history entries
with start_time <= current time.
"""
from typing import List, Dict
import numpy as np
import pandas as pd
from models import FrequencyBand, ScanResult


class FeatureExtractor:
    """Extracts features for ML-based frequency band scheduling."""

    FEATURE_NAMES = [
        "band_id", "center_frequency", "scan_count", "hit_count", "miss_count",
        "hit_rate", "recent_hit_rate", "time_since_last_hit", "time_since_last_scan",
        "estimated_pri", "pri_variance", "mean_pulse_width", "mean_amplitude",
        "frequency_change_rate", "periodicity_score", "scan_density"
    ]

    def __init__(self, bands: List[FrequencyBand]):
        self.bands = bands
        self.feature_names = self.FEATURE_NAMES

    def extract_features(self, band: FrequencyBand, time: float, history: List[ScanResult]) -> dict:
        """Extract features for a single band using ONLY data up to current time."""
        # Filter history to only include scans up to current time (enforce no data leakage)
        band_history = [h for h in history if h.band_id == band.id and h.start_time <= time]

        scan_count = len(band_history)
        hit_count = sum(1 for h in band_history if h.result == 'HIT')
        miss_count = scan_count - hit_count
        hit_rate = hit_count / max(1, scan_count)

        # Recent hit rate (last 10 scans)
        recent = band_history[-10:] if len(band_history) >= 10 else band_history
        recent_hit_rate = sum(1 for h in recent if h.result == 'HIT') / max(1, len(recent))

        # Time since last hit
        hits = [h for h in band_history if h.result == 'HIT']
        time_since_last_hit = (time - hits[-1].start_time) if hits else 999.0

        # Time since last scan
        time_since_last_scan = (time - band_history[-1].start_time) if band_history else 999.0

        # Estimated PRI from hit timing patterns
        estimated_pri = 0.0
        pri_variance = 0.0
        if len(hits) >= 3:
            hit_times = [h.start_time for h in hits]
            intervals = np.diff(hit_times)
            estimated_pri = float(np.mean(intervals))
            pri_variance = float(np.std(intervals))

        # Pulse features from detected pulses
        mean_pulse_width = 0.0
        mean_amplitude = 0.0
        if hits:
            pws = []
            amps = []
            for h in hits:
                for p in h.detected_pulses:
                    if isinstance(p, dict):
                        if 'pw' in p:
                            pws.append(p['pw'])
                        if 'amplitude' in p or 'amp' in p:
                            amps.append(p.get('amplitude', p.get('amp', 0)))
            mean_pulse_width = float(np.mean(pws)) if pws else 0.0
            mean_amplitude = float(np.mean(amps)) if amps else 0.0

        # Frequency change rate (how often different emitters appear)
        detected_emitter_sets = [set(h.detected_emitters) for h in band_history if h.detected_emitters]
        frequency_change_rate = 0.0
        if len(detected_emitter_sets) >= 2:
            changes = sum(1 for i in range(1, len(detected_emitter_sets))
                         if detected_emitter_sets[i] != detected_emitter_sets[i-1])
            frequency_change_rate = changes / len(detected_emitter_sets)

        # Periodicity score (autocorrelation of hit pattern)
        periodicity_score = 0.0
        if len(band_history) >= 10:
            binary_hits = [1 if h.result == 'HIT' else 0 for h in band_history[-50:]]
            if sum(binary_hits) >= 3:
                arr = np.array(binary_hits, dtype=float)
                arr = arr - arr.mean()
                norm = np.dot(arr, arr)
                if norm > 0:
                    autocorr = np.correlate(arr, arr, mode='full')
                    autocorr = autocorr[len(autocorr)//2:]
                    autocorr = autocorr / norm
                    # Look for peaks after lag 1
                    if len(autocorr) > 2:
                        peak_val = np.max(autocorr[1:min(len(autocorr), 20)])
                        periodicity_score = float(max(0, peak_val))

        # Scan density (scans per unit time)
        total_all_scans = max(1, len(history))
        scan_density = scan_count / max(1, total_all_scans)

        return {
            "band_id": band.id,
            "center_frequency": band.center_mhz / 20000.0,  # Normalize
            "scan_count": scan_count,
            "hit_count": hit_count,
            "miss_count": miss_count,
            "hit_rate": round(hit_rate, 4),
            "recent_hit_rate": round(recent_hit_rate, 4),
            "time_since_last_hit": round(min(time_since_last_hit, 999.0), 4),
            "time_since_last_scan": round(min(time_since_last_scan, 999.0), 4),
            "estimated_pri": round(estimated_pri, 6),
            "pri_variance": round(pri_variance, 6),
            "mean_pulse_width": round(mean_pulse_width, 4),
            "mean_amplitude": round(mean_amplitude, 4),
            "frequency_change_rate": round(frequency_change_rate, 4),
            "periodicity_score": round(periodicity_score, 4),
            "scan_density": round(scan_density, 4)
        }

    def extract_all_bands(self, time: float, bands: List[FrequencyBand],
                          history: List[ScanResult]) -> pd.DataFrame:
        """Extract features for all bands. Returns a DataFrame."""
        features = [self.extract_features(b, time, history) for b in bands]
        return pd.DataFrame(features)

    def get_feature_names(self) -> List[str]:
        return self.feature_names
