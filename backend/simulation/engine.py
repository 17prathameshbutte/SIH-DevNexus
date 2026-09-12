from typing import List, Dict
from simulation.environment import RFEnvironment
from simulation.receiver import VirtualReceiver
from models import FrequencyBand, ScanResult

class SimulationEngine:
    def __init__(self, environment: RFEnvironment, receiver: VirtualReceiver, scheduler, bands: List[FrequencyBand], step_duration: float = 0.1, seed: int = 42):
        self.environment = environment
        self.receiver = receiver
        self.scheduler = scheduler
        self.bands = bands
        self.step_duration = step_duration
        self.seed = seed
        self.time = 0.0
        self.step_count = 0
        self.history: List[ScanResult] = []
        
    def start(self) -> dict:
        self.reset()
        return self.get_state()
        
    def step(self) -> dict:
        scheduler_decision = self.scheduler.select_band(self.time, self.bands, self.history)
        selected_band_id = scheduler_decision['selected_band']
        
        band = next(b for b in self.bands if b.id == selected_band_id)
        scan_result = self.receiver.scan(band, self.time, self.step_duration, self.environment)
        self.history.append(scan_result)
        
        self.scheduler.update(scan_result)
        
        step_result = {
            'time': self.time,
            'step': self.step_count,
            'band_id': selected_band_id,
            'result': scan_result.result,
            'detected_emitters': scan_result.detected_emitters,
            'num_pulses': scan_result.num_pulses,
            'scheduler_decision': scheduler_decision
        }
        
        self.time += self.step_duration
        self.step_count += 1
        return step_result
        
    def run(self, num_steps: int = 100) -> dict:
        results = []
        for _ in range(num_steps):
            results.append(self.step())
        return {'results': results, 'state': self.get_state()}
        
    def reset(self):
        self.time = 0.0
        self.step_count = 0
        self.history = []
        self.environment.reset()
        self.scheduler.reset()
        
    def get_state(self) -> dict:
        hits = sum(1 for h in self.history if h.result == 'HIT')
        return {
            'time': self.time,
            'step_count': self.step_count,
            'metrics': {
                'total_scans': len(self.history),
                'hits': hits,
                'misses': len(self.history) - hits
            }
        }
        
    def get_scan_history(self) -> List[dict]:
        return [h.__dict__ for h in self.history]
