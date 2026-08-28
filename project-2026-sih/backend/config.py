from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    h5_dataset_path: str = str(BACKEND_DIR / "data" / "dataset.h5")
    model_path: str = str(BACKEND_DIR / "models" / "smartscan_model.joblib")
    feature_config_path: str = str(BACKEND_DIR / "models" / "feature_config.json")
    prediction_horizon_sec: float = 1.0
    exploration_epsilon: float = 0.10
    random_seed: int = 42
    simulation_step_sec: float = 0.1
    receiver_bandwidth_mhz: float = 200.0
    band_width_mhz: float = 200.0
    min_freq_mhz: float = 2000.0
    max_freq_mhz: float = 18000.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

def get_settings():
    return Settings()
