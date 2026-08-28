from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models import FrequencyBand, ScanResult

class BaseScheduler(ABC):
    @abstractmethod
    def select_band(self, time: float, bands: List[FrequencyBand], history: List[ScanResult]) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def update(self, scan_result: ScanResult):
        pass
        
    @abstractmethod
    def reset(self):
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def get_ranking(self) -> dict:
        return {"rankings": []}

    def get_last_decision(self) -> dict:
        return {}
