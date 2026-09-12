from models import FrequencyBand, ScanResult
from simulation.environment import RFEnvironment

class VirtualReceiver:
    def __init__(self, bandwidth_mhz: float = 200.0):
        self.bandwidth_mhz = bandwidth_mhz
        
    def scan(self, band: FrequencyBand, start_time: float, duration: float, environment: RFEnvironment) -> ScanResult:
        active_emitters = environment.get_active_emitters_in_band(band, start_time)
        pulses = environment.get_pulses(band, start_time, duration)
        
        result_str = 'HIT' if active_emitters or pulses else 'MISS'
        
        return ScanResult(
            band_id=band.id,
            start_time=start_time,
            duration=duration,
            result=result_str,
            detected_emitters=[e.id for e in active_emitters],
            detected_pulses=[{"time": p.time, "freq": p.frequency_mhz} for p in pulses],
            num_pulses=len(pulses)
        )
