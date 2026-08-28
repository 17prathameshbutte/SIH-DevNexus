from typing import List, Dict, Any
from models import FrequencyBand, ScanResult
from schedulers.base import BaseScheduler

class SequentialScheduler(BaseScheduler):
    def __init__(self):
        self.index = 0
        
    def select_band(self, time: float, bands: List[FrequencyBand], history: List[ScanResult]) -> Dict[str, Any]:
        if not bands:
            return {}
        
        band = bands[self.index]
        self.index = (self.index + 1) % len(bands)
        
        ranking = [{"band_id": b.id, "weight": 1.0/len(bands)} for b in bands]
        
        return {
            "selected_band": band.id,
            "probability": 1.0 / len(bands),
            "ranking": ranking,
            "reasoning": {"strategy": "sequential"}
        }
        
    def update(self, scan_result: ScanResult):
        pass
        
    def reset(self):
        self.index = 0
        
    @property
    def name(self) -> str:
        return "SequentialScheduler"
