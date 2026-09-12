from typing import List
import pandas as pd
from models import Emitter, Pulse, FrequencyBand

class Preprocessor:
    def process_emitters(self, raw_data: List[Emitter]) -> List[Emitter]:
        return raw_data
        
    def process_pulses(self, raw_data: List[Pulse]) -> List[Pulse]:
        return sorted(raw_data, key=lambda x: x.time)
        
    def generate_frequency_bands(self, emitters: List[Emitter], band_width_mhz: float=200) -> List[FrequencyBand]:
        if not emitters:
            return []
        min_freq = min(e.frequency_mhz for e in emitters) - band_width_mhz
        max_freq = max(e.frequency_mhz for e in emitters) + band_width_mhz
        
        bands = []
        curr_freq = min_freq
        band_id = 1
        while curr_freq <= max_freq:
            bands.append(FrequencyBand(
                id=band_id,
                lower_mhz=curr_freq,
                upper_mhz=curr_freq + band_width_mhz,
                center_mhz=curr_freq + band_width_mhz/2
            ))
            curr_freq += band_width_mhz
            band_id += 1
        return bands
        
    def normalize_features(self, features_df: pd.DataFrame) -> pd.DataFrame:
        df = features_df.copy()
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
                else:
                    df[col] = 0.0
        return df
