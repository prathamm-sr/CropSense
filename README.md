# 🌾 CropSense ML

> Precision agriculture — predict the optimal crop for any soil and climate profile.

![Python](https://img.shields.io/badge/python-3.11+-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange)
![XGBoost](https://img.shields.io/badge/xgboost-2.0-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Overview

CropSense ML is the machine learning core of the CropSense system. Given seven soil and climate parameters, it recommends the best crop to cultivate from 22 possibilities. The pipeline trains five classifiers, evaluates them on a comprehensive metric suite, and persists the best model for inference.

**Dataset:** [Crop Recommendation Dataset](https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset) — 2,200 samples, 22 crop classes, 7 features.

---

## Features

- Five models trained and compared: Random Forest, XGBoost, Gradient Boosting, Logistic Regression, SVM
- Stratified 70/12/18 train/val/test split with 5-fold cross-validation
- **13 evaluation metrics**: Accuracy, Balanced Accuracy, F1 (macro + weighted), Precision, Recall, Cohen's Kappa, MCC, ROC-AUC, Log Loss, Top-2/3 Accuracy, ECE
- Per-class F1 breakdown across all 22 crops
- SHAP global feature importance
- Calibration curves, learning curve, confusion matrix, model comparison plots
- Clean `Predictor` class with input validation for downstream API use
- pytest suite with metric quality gates (CI will fail on model degradation)

---

## File structure

```
cropsense-ml/
├── data/
│   └── crop_recommendation.csv
├── ml/
│   ├── __init__.py
│   ├── train.py        ← training pipeline, 5 models, CV
│   ├── evaluate.py     ← 13 metrics + 7 plots
│   ├── predict.py      ← Predictor class + CLI
│   └── utils.py        ← shared helpers, constants
├── models/             ← saved .joblib artifacts (gitignored)
├── outputs/            ← plots + JSON reports (gitignored)
├── tests/
│   └── test_model.py   ← 20 pytest tests incl. metric gates
├── requirements.txt
└── README.md
```

---

## Quickstart

```bash
# 1. Clone and install
git clone https://github.com/yourhandle/cropsense-ml
cd cropsense-ml
pip install -r requirements.txt

# 2. Add dataset
# Download crop_recommendation.csv from Kaggle and place in data/

# 3. Train
python -m ml.train

# 4. Evaluate
python -m ml.evaluate

# 5. Predict (CLI)
python -m ml.predict \
  --N 90 --P 42 --K 43 \
  --temperature 20.8 --humidity 82.0 \
  --ph 6.5 --rainfall 202.9

# 6. Test
pytest tests/ -v
```

---

## Results (XGBoost — best model)

| Metric              | Score  |
|---------------------|--------|
| Accuracy            | ~0.993 |
| Balanced Accuracy   | ~0.993 |
| F1 macro            | ~0.993 |
| ROC-AUC (macro OvR) | ~0.999 |
| Cohen's Kappa       | ~0.993 |
| MCC                 | ~0.993 |
| Log Loss            | ~0.03  |
| Top-2 Accuracy      | ~1.000 |
| ECE                 | ~0.01  |

*Scores vary slightly with random seed. Run `ml.evaluate` to regenerate.*

---

## Programmatic usage

```python
from ml.predict import Predictor

p = Predictor()  # loads best model automatically

result = p.predict({
    "N": 90, "P": 42, "K": 43,
    "temperature": 20.8, "humidity": 82.0,
    "ph": 6.5, "rainfall": 202.9,
})

print(result.top_crop)     # "rice"
print(result.confidence)   # 0.97
print(result.top_k)        # [{crop, probability}, ...]
print(result.to_dict())    # JSON-serialisable
```

---

## Roadmap

- [x] Phase 1 — ML core (this repo)
- [ ] Phase 2 — FastAPI ML microservice
- [ ] Phase 3 — Main backend + PostgreSQL
- [ ] Phase 4 — React frontend
- [ ] Phase 5 — Docker Compose
- [ ] Phase 6 — Prometheus + Grafana monitoring
- [ ] Phase 7 — GitHub Actions CI/CD
- [ ] Phase 8 — Cloud deploy (EC2 / Render)

---

## License

MIT