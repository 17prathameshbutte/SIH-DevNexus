"""ML predictor for SmartScan-EW scheduler."""
import os
import joblib
import json
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Predictor:
    """Loads a trained ML model and makes predictions."""

    def __init__(self, model_path: str, feature_config_path: str = None):
        self.model = None
        self.feature_names = []

        # Load model
        try:
            if model_path and os.path.exists(model_path):
                self.model = joblib.load(model_path)
                logger.info(f"Loaded model from {model_path}")
            else:
                logger.warning(f"Model file not found: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")

        # Load feature config
        if feature_config_path is None and model_path:
            feature_config_path = model_path.replace('.joblib', '_features.json')

        try:
            if feature_config_path and os.path.exists(feature_config_path):
                with open(feature_config_path, 'r') as f:
                    config = json.load(f)
                # Handle both formats: list or dict with 'feature_names' key
                if isinstance(config, list):
                    self.feature_names = config
                elif isinstance(config, dict) and 'feature_names' in config:
                    self.feature_names = config['feature_names']
                else:
                    self.feature_names = list(config.keys()) if isinstance(config, dict) else []
                logger.info(f"Loaded {len(self.feature_names)} feature names")
            else:
                logger.warning(f"Feature config not found: {feature_config_path}")
        except Exception as e:
            logger.error(f"Failed to load feature config: {e}")

    def predict(self, features_df: pd.DataFrame) -> np.ndarray:
        """Predict activity probability for each row in features_df."""
        if self.model is None:
            return np.full(len(features_df), 0.5)

        try:
            # Use feature names to select columns, fallback to all columns
            if self.feature_names:
                available = [f for f in self.feature_names if f in features_df.columns]
                if available:
                    X = features_df[available]
                else:
                    X = features_df
            else:
                X = features_df

            if hasattr(self.model, 'predict_proba'):
                probs = self.model.predict_proba(X)
                if probs.shape[1] >= 2:
                    return probs[:, 1]
                return probs[:, 0]
            else:
                return self.model.predict(X).astype(float)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return np.full(len(features_df), 0.5)

    def predict_single(self, features_dict: dict) -> float:
        """Predict probability for a single feature vector."""
        df = pd.DataFrame([features_dict])
        probs = self.predict(df)
        return float(probs[0])

    def get_feature_importances(self) -> dict:
        """Return feature importance dict."""
        if self.model is None:
            return {}
        try:
            if hasattr(self.model, 'feature_importances_'):
                names = self.feature_names if self.feature_names else [f"f{i}" for i in range(len(self.model.feature_importances_))]
                return {f: round(float(i), 4) for f, i in zip(names, self.model.feature_importances_)}
        except Exception:
            pass
        return {}
