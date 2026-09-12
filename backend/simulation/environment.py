import random
import math
from typing import List
from models import Emitter, Pulse, FrequencyBand

class RFEnvironment:
    def __init__(self, emitters: List[Emitter], pulses: List[Pulse], seed: int = 42):
        self.emitters = emitters
        self.pulses = sorted(pulses, key=lambda x: x.time) if pulses else []
        self.seed = seed
        self.rng = random.Random(seed)
        
    def get_state(self, time: float) -> dict:
        return {e.id: self._is_emitter_active(e, time) for e in self.emitters}
        
    def is_active(self, band: FrequencyBand, time: float) -> bool:
        return len(self.get_active_emitters_in_band(band, time)) > 0
        
    def get_active_emitters(self, time: float) -> List[Emitter]:
        return [e for e in self.emitters if self._is_emitter_active(e, time)]
        
    def get_active_emitters_in_band(self, band: FrequencyBand, time: float) -> List[Emitter]:
        return [e for e in self.get_active_emitters(time) if band.lower_mhz <= e.frequency_mhz <= band.upper_mhz]
        
    def get_pulses(self, band: FrequencyBand, start_time: float, duration: float) -> List[Pulse]:
        end_time = start_time + duration
        if self.pulses:
            return [p for p in self.pulses if start_time <= p.time <= end_time and band.lower_mhz <= p.frequency_mhz <= band.upper_mhz]
        
        # Simulate pulses
        generated_pulses = []
        for e in self.emitters:
            if band.lower_mhz <= e.frequency_mhz <= band.upper_mhz:
                if self._is_emitter_active(e, start_time):
                    # simple pulse simulation
                    generated_pulses.append(Pulse(
                        time=start_time,
                        frequency_mhz=e.frequency_mhz,
                        pulse_width_us=e.pulse_width_us,
                        aoa_deg=0.0,
                        amplitude=e.power_dbm,
                        emitter_id=e.id
                    ))
        return generated_pulses
        
    def _is_emitter_active(self, emitter: Emitter, time: float) -> bool:
        if not emitter.active:
            return False
        
        t_us = time * 1e6
        if emitter.emitter_type == 'periodic':
            return (t_us % emitter.pri_us) < emitter.pulse_width_us
        elif emitter.emitter_type == 'frequency_agile':
            # Simplified: frequency agile changes frequencies but let's assume it's active in its primary frequency based on a slower clock
            period = emitter.pri_us * 10
            return (t_us % period) < (period / 2)
        elif emitter.emitter_type == 'intermittent':
            period = 5_000_000 # 5 seconds
            return (t_us % period) < 1_000_000
        else:
            return (t_us % emitter.pri_us) < emitter.pulse_width_us

    def reset(self):
        self.rng = random.Random(self.seed)
