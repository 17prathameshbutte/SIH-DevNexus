# Integrated AIML Code

This folder contains the AIML implementation synchronized from `mll_code/ML Data Pipeline Prathemesh`.

## Familiar code brought into the project

- `ml_engine/model.py`: dual-head PyTorch scheduler for dwell time and next-band prediction.
- `ml_engine/api_wrapper.py`: model loading, scheduler inference, and optional DBSCAN anomaly flags.
- `ml_engine/anomaly_detector.py`: DBSCAN-based uncatalogued-signal detection.
- `ml_engine/preprocessing.py`: PDW scaling and diagnostic-log preprocessing.
- `dataset_pipeline/dataset_preprocessing.py`: numeric StandardScaler plus receiver-mode TF-IDF features.
- `dataset_pipeline/pulse_classifier.py`: PyTorch MLP emitter classifier.
- `dataset_pipeline/export_pkl.py`, `hf_dataset_loader.py`, and `metrics_evaluator.py`: model export, dataset normalization, and evaluation helpers.

The scheduler files remain usable in both documented modes:

```bash
cd backend/ml_pipeline/ml_engine
python train.py
python export_pkl.py
python test_ml_standalone.py
```

The dataset classifier workflow is:

```bash
cd backend/ml_pipeline/dataset_pipeline
python hf_dataset_loader.py
python pulse_classifier.py
python export_pkl.py
```

## Project integration added here

The original project already had a FastAPI simulation and a Random Forest feature
scheduler. The following integration code is project-specific rather than part
of the copied standalone AIML implementation:

- `backend/api/ml_pipeline.py` validates FastAPI request shapes and exposes the
  standalone scheduler at `/api/ml/pipeline`.
- The import fallback in `ml_engine/api_wrapper.py` lets the same familiar file
  run as a package under FastAPI and directly as a standalone script.
- The existing `backend/ml/predict.py` and `backend/ml/features.py` path remains
  available for the original simulation scheduler.

The scheduler prediction contract is returned with `status`, dwell time, next
band, confidence, optional anomaly flags, and an error field. Missing exported
pickle weights fall back to the supplied `.pth` weights so smoke tests remain
runnable.
