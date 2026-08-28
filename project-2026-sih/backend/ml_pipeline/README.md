# Smart Scan Strategy for Electronic Warfare — SIH 55

Two independent, standalone deliverables as `.py` files (no notebooks), built
from the patterns in your ANN/DBSCAN/REGEX practice notebooks.

## 1. `ml_engine/` — core scheduling brain + anomaly detector (local mock data)

| File | What it does |
|---|---|
| `mock_rf_feed.py` | Generates mock `(B, C, T)` = (batch, 10 channels, 50 timesteps) occupancy tensors + raw PDW batches. |
| `preprocessing.py` | `StandardScaler` for PDW features; Regex + NLTK cleaning for diagnostic error logs. |
| `anomaly_detector.py` | `DBSCAN(eps=0.3, min_samples=5)` + auto-eps via k-NN distance knee; flags `-1` = uncatalogued/frequency-hopping signal. |
| `model.py` | `SmartScanScheduler(nn.Module)`: shared trunk `Linear→ReLU→Linear→ReLU`, dual heads — dwell time (regression) + next band (classification). |
| `train.py` | 5-step training loop (`zero_grad → forward → loss → backward → step`), saves `smart_scan_v1.pth`. |
| `export_pkl.py` | Exports the trained model as **`smart_scan_v1.pkl`** (state_dict + architecture bundled via `pickle`) — this is the final deliverable format. |
| `api_wrapper.py` | `predict_step(input_json)` → defined JSON contract (dwell time, next band, band confidence, anomaly flags). Loads from `.pkl` (falls back to `.pth` if the pkl hasn't been exported). |
| `test_ml_standalone.py` | Generates a mock input JSON, loads it, calls `predict_step()`, asserts it works. |

Run order:
```bash
cd ml_engine
python train.py              # produces smart_scan_v1.pth
python export_pkl.py         # produces smart_scan_v1.pkl  <-- final model file
python test_ml_standalone.py # end-to-end smoke test (loads the .pkl)
```

**`smart_scan_v1.pkl` contents** (loaded via `pickle.load`):
```python
{
  "state_dict": <PyTorch state_dict>,
  "architecture": {"input_dim": 500, "num_bands": 10, "hidden_dims": (128, 64)},
  "model_class": "SmartScanScheduler",
}
```
Reconstruct with `SmartScanScheduler(**bundle["architecture"])` then `.load_state_dict(bundle["state_dict"])` — see `load_from_pkl()` in `export_pkl.py`.

## 2. `dataset_pipeline/` — Hugging Face PDW dataset + classification + metrics

| File | What it does |
|---|---|
| `hf_dataset_loader.py` | Downloads/parses `alan-turing-institute/turing-synthetic-radar-dataset`, normalizes PDW columns (ToA, Center Frequency, Pulse Width, AoA, Amplitude), exports `test_pdw_sample.csv`. |
| `dataset_preprocessing.py` | `StandardScaler` on numeric PDW channels + `TfidfVectorizer` on categorical radar-mode tags. |
| `pulse_classifier.py` | PyTorch MLP (`nn.CrossEntropyLoss`) classifying pulse trains into emitter/threat categories. |
| `export_pkl.py` | Exports the trained classifier as **`pulse_classifier.pkl`** (state_dict + architecture + the fitted `StandardScaler`/`TfidfVectorizer` needed for inference). |
| `metrics_evaluator.py` | Computes **P_int** (probability of detection), **P_fa** (false alarm rate), and **average intercept time error** from predicted vs. actual lists. |

**⚠️ Important — dataset access:** the Turing Synthetic Radar Dataset is
**gated** on Hugging Face. Before `hf_dataset_loader.py` will pull real data
you need to:
1. Log in at the [dataset page](https://huggingface.co/datasets/alan-turing-institute/turing-synthetic-radar-dataset) and accept the access conditions.
2. `pip install datasets huggingface_hub`
3. `huggingface-cli login` (or `export HF_TOKEN=hf_xxx`)

I couldn't reach `huggingface.co` from this sandbox to confirm the exact
column/config names, so `hf_dataset_loader.py` normalizes several likely
column-name variants (see `COLUMN_ALIASES`) and **falls back to a synthetic
PDW sample** if the real dataset isn't reachable, so the rest of the pipeline
(`dataset_preprocessing.py` → `pulse_classifier.py` → `metrics_evaluator.py`)
stays runnable end-to-end even before you've set up HF auth. Once you run it
for real, check the printed `df.head()` — if any PDW column doesn't map
correctly, add its real name to `COLUMN_ALIASES` in `hf_dataset_loader.py`.

Run order:
```bash
cd dataset_pipeline
python hf_dataset_loader.py       # -> test_pdw_sample.csv
python pulse_classifier.py        # -> pulse_classifier.pth, prints accuracy
python export_pkl.py              # -> pulse_classifier.pkl  <-- final model file
python metrics_evaluator.py       # prints P_int / P_fa / time-error demo
```

## Setup

```bash
pip install -r requirements.txt
```

Both pipelines were run end-to-end in this environment and confirmed working
(training converges, `predict_step()` returns the JSON contract, metrics
compute correctly) — `dataset_pipeline` was verified using its synthetic
fallback since this sandbox can't reach `huggingface.co`.
