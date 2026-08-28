import random
from typing import List, Dict, Any
from models import FrequencyBand, ScanResult
from schedulers.base import BaseScheduler

class RandomScheduler(BaseScheduler):
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        
    def select_band(self, time: float, bands: List[FrequencyBand], history: List[ScanResult]) -> Dict[str, Any]:
        if not bands:
            return {}
            
        band = self.rng.choice(bands)
        
        ranking = [{"band_id": b.id, "weight": 1.0/len(bands)} for b in bands]
        
        return {
            "selected_band": band.id,
            "probability": 1.0 / len(bands),
            "ranking": ranking,
            "reasoning": {"strategy": "random"}
        }
        
    def update(self, scan_result: ScanResult):
        pass
        
    def reset(self):
        self.rng = random.Random(self.seed)
        
    @property
    def name(self) -> str:
        return "RandomScheduler"
