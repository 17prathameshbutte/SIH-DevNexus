"""ML model training pipeline for SmartScan-EW."""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def load_training_data(filepath: str):
    """Load training data from parquet file."""
    df = pd.read_parquet(filepath)
    feature_cols = [c for c in df.columns if c != 'target']
    X = df[feature_cols]
    y = df['target']
    return X, y, feature_cols


def train_model(X=None, y=None, feature_cols=None,
                h5_path=None, model_path=None, bands=None, prediction_horizon=1.0):
    """Train ML model. Can be called from API or CLI."""

    # If no data provided, build it
    if X is None:
        from data.h5_loader import H5Loader
        from data.preprocessor import Preprocessor
        from simulation.environment import RFEnvironment
        from simulation.receiver import VirtualReceiver
        from simulation.frequency_bands import FrequencyBandManager
        from ml.build_training_data import TrainingDataBuilder

        h5_path = h5_path or './data/dataset.h5'
        model_path = model_path or './models/smartscan_model.joblib'

        print(f"Loading dataset from {h5_path}...")
        loader = H5Loader()
        data = loader.load(h5_path)
        emitters = data.get('emitters', [])
        pulses = data.get('pulses', [])

        if not emitters:
            return {"status": "error", "detail": "No emitters found in dataset"}

        preprocessor = Preprocessor()
        if bands is None:
            bands = preprocessor.generate_frequency_bands(emitters)

        environment = RFEnvironment(emitters, pulses, seed=42)
        receiver = VirtualReceiver(bandwidth_mhz=200.0)

        print("Building training data...")
        builder = TrainingDataBuilder(
            environment, receiver, bands,
            prediction_horizon=prediction_horizon,
            step_duration=0.1
        )
        df = builder.build(num_steps=500, seed=42)

        feature_cols = [c for c in df.columns if c != 'target']
        X = df[feature_cols]
        y = df['target']

    print(f"Training data shape: {X.shape}, target distribution: {dict(y.value_counts())}")

    # Time-based split (first 70% train, last 30% test) - NO random split to prevent data leakage
    split_idx = int(len(X) * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # Try XGBoost first, fallback to RandomForest
    try:
        import xgboost as xgb
        print("Training XGBoost classifier...")
        model = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
    except ImportError:
        print("XGBoost not available, using RandomForest...")
        model = RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )

    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else preds.astype(float)

    metrics = {
        'status': 'success',
        'accuracy': round(float(accuracy_score(y_test, preds)), 4),
        'precision': round(float(precision_score(y_test, preds, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, preds, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, preds, zero_division=0)), 4),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_importances': {},
        'model_type': type(model).__name__
    }

    # Feature importances
    if hasattr(model, 'feature_importances_'):
        importances = {f: round(float(i), 4) for f, i in zip(feature_cols, model.feature_importances_)}
        metrics['feature_importances'] = dict(sorted(importances.items(), key=lambda x: -x[1]))

    # Save model
    model_path = model_path or './models/smartscan_model.joblib'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(model, model_path)
    metrics['model_path'] = model_path
    print(f"Model saved to {model_path}")

    # Save feature config
    feature_config_path = model_path.replace('.joblib', '_features.json')
    feature_config = {
        'feature_names': list(feature_cols),
        'num_features': len(feature_cols),
        'model_type': type(model).__name__
    }
    with open(feature_config_path, 'w') as fout:
        json.dump(feature_config, fout, indent=2)
    metrics['feature_config_path'] = feature_config_path
    print(f"Feature config saved to {feature_config_path}")

    print(f"\n=== Training Results ===")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print(f"Model:     {metrics['model_type']}")

    return metrics


def save_model(model, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)


def save_feature_config(feature_names, filepath: str):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump({'feature_names': list(feature_names)}, f, indent=2)


if __name__ == '__main__':
    result = train_model()
    print(f"\nTraining complete: {result}")
