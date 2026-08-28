"""Metrics and ML training API endpoints."""
from fastapi import APIRouter, HTTPException
from app_state import app_state
from evaluation.metrics import MetricsEngine
from evaluation.comparison import ComparisonEngine

router = APIRouter(prefix='/api', tags=['metrics'])

@router.get('/metrics')
def get_metrics():
    if not app_state.engine:
        # Return empty metrics if no simulation running
        return MetricsEngine()._empty_metrics()
    try:
        engine = MetricsEngine()
        time_range = (0, app_state.engine.time)
        # get_scan_history returns list of dicts, but we need ScanResult objects
        return engine.calculate(
            app_state.engine.history,
            app_state.environment,
            app_state.bands,
            time_range
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/comparison')
def run_comparison():
    try:
        model_path = app_state.settings.model_path if app_state.settings else None
        feature_config_path = model_path.replace('.joblib', '_features.json') if model_path else None
        comp_engine = ComparisonEngine(
            app_state.environment,
            app_state.receiver,
            app_state.bands,
            num_steps=200,
            step_duration=app_state.settings.simulation_step_sec if app_state.settings else 0.1,
            model_path=model_path,
            feature_config_path=feature_config_path
        )
        seed = app_state.settings.random_seed if app_state.settings else 42
        return comp_engine.run_comparison(seed)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/ml/train')
def trigger_training():
    try:
        from ml.train import train_model
        result = train_model(
            h5_path=app_state.settings.h5_dataset_path if app_state.settings else None,
            model_path=app_state.settings.model_path if app_state.settings else None,
            bands=app_state.bands,
            prediction_horizon=app_state.settings.prediction_horizon_sec if app_state.settings else 1.0
        )

        # Reload model into app state
        if result.get('status') == 'success':
            try:
                from ml.predict import Predictor
                from ml.features import FeatureExtractor
                model_path = result.get('model_path', app_state.settings.model_path)
                feature_config_path = result.get('feature_config_path', model_path.replace('.joblib', '_features.json'))
                app_state.predictor = Predictor(model_path, feature_config_path)
                app_state.feature_extractor = FeatureExtractor(app_state.bands)
                app_state.model_loaded = True
            except Exception as e:
                print(f"Failed to reload model: {e}")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/ml/status')
def ml_status():
    result = {
        'model_loaded': app_state.model_loaded,
        'model_path': app_state.settings.model_path if app_state.settings else None,
        'feature_count': 0,
        'accuracy': None,
        'feature_importances': {}
    }

    if app_state.predictor and app_state.predictor.model is not None:
        result['feature_count'] = len(app_state.predictor.feature_names)
        result['feature_importances'] = app_state.predictor.get_feature_importances()

    return result
