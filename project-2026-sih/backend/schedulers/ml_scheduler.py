"""SmartScan ML Scheduler with explainable priority scoring."""
import random
from typing import List, Dict, Any
import numpy as np
from models import FrequencyBand, ScanResult
from schedulers.base import BaseScheduler


class MLScheduler(BaseScheduler):
    """ML-based scheduler that predicts which frequency band is most likely to contain an active emitter."""

    def __init__(self, predictor, feature_extractor, epsilon: float = 0.10, seed: int = 42):
        self.predictor = predictor
        self.feature_extractor = feature_extractor
        self.epsilon = epsilon
        self.seed = seed
        self.rng = random.Random(seed)
        self._last_decision = {}
        self._scan_counts = {}
        self._last_ranking = []

    def select_band(self, time: float, bands: List[FrequencyBand], history: List[ScanResult]) -> Dict[str, Any]:
        if not bands:
            return {"selected_band": 0, "probability": 0, "ranking": [], "reasoning": {}}

        # Extract features for all bands (ONLY using historical data up to current time)
        features_df = self.feature_extractor.extract_all_bands(time, bands, history)

        # Get ML probabilities
        ml_probs = self.predictor.predict(features_df)

        # Build ranking with explainable priority scores
        ranking = []
        for i, band in enumerate(bands):
            ml_prob = float(ml_probs[i]) if ml_probs is not None and i < len(ml_probs) else 0.0

            # Calculate component scores
            band_history = [h for h in history if h.band_id == band.id]
            recent = band_history[-10:] if len(band_history) >= 10 else band_history
            recent_hit_rate = sum(1 for h in recent if h.result == 'HIT') / max(1, len(recent)) if recent else 0.0

            # Periodicity confidence
            hits = [h for h in band_history if h.result == 'HIT']
            periodicity_confidence = 0.0
            if len(hits) >= 3:
                intervals = [hits[j+1].start_time - hits[j].start_time for j in range(len(hits)-1)]
                if intervals:
                    mean_interval = np.mean(intervals)
                    std_interval = np.std(intervals)
                    periodicity_confidence = max(0, 1 - std_interval / max(0.001, mean_interval))

            # Exploration bonus (favor under-explored bands)
            scan_count = self._scan_counts.get(band.id, 0)
            total_scans = max(1, sum(self._scan_counts.values())) if self._scan_counts else 1
            expected_scans = total_scans / len(bands)
            exploration_bonus = max(0, (expected_scans - scan_count) / max(1, expected_scans)) * 0.2

            # Weighted priority score
            priority_score = (
                0.50 * ml_prob +
                0.20 * recent_hit_rate +
                0.15 * periodicity_confidence +
                0.15 * exploration_bonus
            )

            # Recommendation label
            if priority_score > 0.7:
                recommendation = "HIGH PRIORITY"
            elif priority_score > 0.4:
                recommendation = "MEDIUM"
            elif exploration_bonus > 0.1:
                recommendation = "EXPLORATION"
            else:
                recommendation = "LOW"

            ranking.append({
                "band_id": band.id,
                "center_mhz": band.center_mhz,
                "probability": round(ml_prob, 4),
                "priority_score": round(priority_score, 4),
                "components": {
                    "ml_probability": round(ml_prob, 4),
                    "recent_activity": round(recent_hit_rate, 4),
                    "periodicity_confidence": round(periodicity_confidence, 4),
                    "exploration_bonus": round(exploration_bonus, 4)
                },
                "recommendation": recommendation
            })

        # Sort by priority score
        ranking.sort(key=lambda x: x["priority_score"], reverse=True)
        self._last_ranking = ranking

        # Epsilon-greedy selection
        is_exploration = False
        if self.rng.random() < self.epsilon:
            # Explore: pick an under-explored band
            under_explored = sorted(ranking, key=lambda x: self._scan_counts.get(x["band_id"], 0))
            selected = under_explored[0]["band_id"]
            is_exploration = True
        else:
            # Exploit: pick highest priority
            selected = ranking[0]["band_id"]

        # Track scan counts
        self._scan_counts[selected] = self._scan_counts.get(selected, 0) + 1

        selected_info = next(r for r in ranking if r["band_id"] == selected)

        self._last_decision = {
            "selected_band": selected,
            "probability": selected_info["probability"],
            "ranking": ranking[:10],  # Top 10
            "reasoning": {
                "ml_probability": selected_info["components"]["ml_probability"],
                "recent_activity": selected_info["components"]["recent_activity"],
                "periodicity_confidence": selected_info["components"]["periodicity_confidence"],
                "exploration_bonus": selected_info["components"]["exploration_bonus"],
                "final_priority": selected_info["priority_score"],
                "recommendation": selected_info["recommendation"],
                "is_exploration": is_exploration,
                "epsilon": self.epsilon
            }
        }

        return self._last_decision

    def update(self, scan_result: ScanResult):
        """Update internal state after scan result."""
        pass  # History is maintained by the engine

    def reset(self):
        self.rng = random.Random(self.seed)
        self._last_decision = {}
        self._scan_counts = {}
        self._last_ranking = []

    def get_ranking(self):
        return {"rankings": self._last_ranking}

    def get_last_decision(self):
        return self._last_decision

    @property
    def name(self) -> str:
        return "SmartScan"
