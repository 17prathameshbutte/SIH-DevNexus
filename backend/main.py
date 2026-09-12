"""SmartScan-EW FastAPI Backend Application."""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app_state import app_state
from config import get_settings
from data.h5_loader import H5Loader
from data.preprocessor import Preprocessor
from simulation.frequency_bands import FrequencyBandManager
from simulation.environment import RFEnvironment
from simulation.receiver import VirtualReceiver
from schedulers.sequential_scheduler import SequentialScheduler

from api.dataset import router as dataset_router
from api.simulation import router as simulation_router
from api.scheduler import router as scheduler_router
from api.metrics import router as metrics_router
from api.websocket import router as websocket_router
from api.ml_pipeline import router as ml_pipeline_router

app = FastAPI(
    title='SmartScan-EW API',
    description='ML-based Electronic Support receiver scheduler for intelligent frequency scanning',
    version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dataset_router)
app.include_router(simulation_router)
app.include_router(scheduler_router)
app.include_router(metrics_router)
app.include_router(websocket_router)
app.include_router(ml_pipeline_router)

@app.on_event("startup")
async def startup_event():
    """Initialize application state on startup."""
    print("=" * 60)
    print("  SmartScan-EW Backend Starting...")
    print("=" * 60)

    app_state.settings = get_settings()
    settings = app_state.settings

    # Generate sample dataset if it doesn't exist
    h5_path = settings.h5_dataset_path
    if not os.path.exists(h5_path):
        print(f"Dataset not found at {h5_path}, generating sample...")
        try:
            from scripts.generate_sample_h5 import generate
            generate(h5_path)
            print(f"Sample dataset generated at {h5_path}")
        except Exception as e:
            print(f"Failed to generate sample dataset: {e}")

    # Load dataset
    try:
        loader = H5Loader()
        data = loader.load(h5_path)
        app_state.emitters = data.get('emitters', [])
        app_state.pulses = data.get('pulses', [])
        print(f"Loaded {len(app_state.emitters)} emitters, {len(app_state.pulses)} pulses")
    except Exception as e:
        print(f"Failed to load H5 dataset: {e}")

    # Generate frequency bands
    try:
        preprocessor = Preprocessor()
        if app_state.emitters:
            app_state.bands = preprocessor.generate_frequency_bands(
                app_state.emitters, settings.band_width_mhz
            )
        else:
            bm = FrequencyBandManager.from_range(
                settings.min_freq_mhz, settings.max_freq_mhz, settings.band_width_mhz
            )
            app_state.bands = bm.get_all_bands()
        app_state.band_manager = FrequencyBandManager(app_state.bands)
        print(f"Generated {len(app_state.bands)} frequency bands")
    except Exception as e:
        print(f"Failed to generate bands: {e}")
        bm = FrequencyBandManager.from_range(
            settings.min_freq_mhz, settings.max_freq_mhz, settings.band_width_mhz
        )
        app_state.bands = bm.get_all_bands()
        app_state.band_manager = bm

    # Setup simulation environment
    app_state.environment = RFEnvironment(
        app_state.emitters, app_state.pulses, settings.random_seed
    )
    app_state.receiver = VirtualReceiver(settings.receiver_bandwidth_mhz)

    # Try loading ML model
    try:
        model_path = settings.model_path
        feature_config_path = model_path.replace('.joblib', '_features.json')
        if os.path.exists(model_path):
            from ml.predict import Predictor
            from ml.features import FeatureExtractor
            app_state.predictor = Predictor(model_path, feature_config_path)
            app_state.feature_extractor = FeatureExtractor(app_state.bands)
            app_state.model_loaded = True
            print(f"ML model loaded from {model_path}")
        else:
            print(f"No ML model found at {model_path} (train with POST /api/ml/train)")
    except Exception as e:
        print(f"Failed to load ML model: {e}")

    # Default scheduler
    app_state.current_scheduler = SequentialScheduler()

    print("=" * 60)
    print("  SmartScan-EW Backend Ready!")
    print(f"  Emitters: {len(app_state.emitters)}")
    print(f"  Bands: {len(app_state.bands)}")
    print(f"  Model loaded: {app_state.model_loaded}")
    print("=" * 60)

@app.get('/api/health')
def health_check():
    return {
        "status": "healthy",
        "emitters_loaded": len(app_state.emitters),
        "bands_count": len(app_state.bands),
        "model_loaded": app_state.model_loaded
    }
