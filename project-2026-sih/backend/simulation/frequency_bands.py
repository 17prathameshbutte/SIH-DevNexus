from typing import List, Optional
from models import FrequencyBand

class FrequencyBandManager:
    def __init__(self, bands: List[FrequencyBand]):
        self.bands = {b.id: b for b in bands}
        
    def get_band(self, band_id: int) -> FrequencyBand:
        return self.bands.get(band_id)
        
    def get_band_for_frequency(self, freq_mhz: float) -> Optional[FrequencyBand]:
        for b in self.bands.values():
            if b.lower_mhz <= freq_mhz <= b.upper_mhz:
                return b
        return None
        
    def get_all_bands(self) -> List[FrequencyBand]:
        return list(self.bands.values())
        
    def to_dict_list(self) -> List[dict]:
        return [{"id": b.id, "lower_mhz": b.lower_mhz, "upper_mhz": b.upper_mhz, "center_mhz": b.center_mhz} for b in self.bands.values()]
        
    @classmethod
    def from_range(cls, min_freq: float, max_freq: float, bandwidth: float):
        bands = []
        curr = min_freq
        bid = 1
        while curr < max_freq:
            bands.append(FrequencyBand(
                id=bid,
                lower_mhz=curr,
                upper_mhz=curr + bandwidth,
                center_mhz=curr + bandwidth / 2
            ))
            curr += bandwidth
            bid += 1
        return cls(bands)
