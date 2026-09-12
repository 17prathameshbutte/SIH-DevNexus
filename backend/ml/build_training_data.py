import pandas as pd
from simulation.environment import RFEnvironment
from simulation.receiver import VirtualReceiver
from schedulers.sequential_scheduler import SequentialScheduler
from ml.features import FeatureExtractor

class TrainingDataBuilder:
    def __init__(self, environment: RFEnvironment, receiver: VirtualReceiver, bands, prediction_horizon: float = 1.0, step_duration: float = 0.1):
        self.environment = environment
        self.receiver = receiver
        self.bands = bands
        self.prediction_horizon = prediction_horizon
        self.step_duration = step_duration
        self.feature_extractor = FeatureExtractor(bands)
        
    def build(self, num_steps: int = 500, seed: int = 42) -> pd.DataFrame:
        self.environment.reset()
        scheduler = SequentialScheduler()
        history = []
        time = 0.0
        
        all_features = []
        
        for _ in range(num_steps):
            # Extract features for all bands at current time BEFORE scanning
            features_df = self.feature_extractor.extract_all_bands(time, self.bands, history)
            
            # Target generation
            targets = []
            for b in self.bands:
                # Target: is there activity in [t, t + prediction_horizon]
                future_time_end = time + self.prediction_horizon
                
                # Check environment
                is_active = any(self.environment.is_active(b, t) for t in [time + i*0.1 for i in range(1, int(self.prediction_horizon/0.1) + 1)])
                targets.append(1 if is_active else 0)
                
            features_df['target'] = targets
            all_features.append(features_df)
            
            # Step the simulation
            decision = scheduler.select_band(time, self.bands, history)
            selected_band = next(b for b in self.bands if b.id == decision['selected_band'])
            scan_result = self.receiver.scan(selected_band, time, self.step_duration, self.environment)
            history.append(scan_result)
            
            time += self.step_duration
            
        final_df = pd.concat(all_features, ignore_index=True)
        return final_df
        
    def save(self, df: pd.DataFrame, filepath: str):
        df.to_parquet(filepath)

if __name__ == '__main__':
    print("Training data builder main block")
