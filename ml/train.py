"""
train.py
--------
Trains multiple classifiers on the crop recommendation dataset,
selects the best by validation accuracy, saves all models + metadata.

Usage:
    python -m ml.train
    python -m ml.train --data data/crop_recommendation.csv --seed 42
"""

import argparse
import json
import os
import time
import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score,
)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from xgboost import XGBClassifier

from ml.utils import (
    FEATURE_COLS,
    TARGET_COL,
    load_data,
    save_model,
    save_json,
    set_seed,
    OUTPUTS_DIR,
)

warnings.filterwarnings("ignore")


def build_models() -> dict:
    """Return a dict of name → sklearn-compatible estimator (wrapped in pipeline where scaling needed)."""
    return {
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            max_features="sqrt",
            random_state=42,
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="mlogloss",
            random_state=42,
            verbosity=0,
        ),
        "gradient_boosting": GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            random_state=42,
        ),
        "logistic_regression": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(
                max_iter=1000,
                C=1.0,
                solver="lbfgs",
                random_state=42,
            )),
        ]),
        "svm": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", SVC(
                kernel="rbf",
                C=10,
                gamma="scale",
                probability=True,
                random_state=42,
            )),
        ]),
    }


def train(data_path: str | None = None, seed: int = 42, cv_folds: int = 5) -> dict:
    set_seed(seed)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # ── Load & split ──────────────────────────────────────────────────────────
    df = load_data(data_path)
    X = df[FEATURE_COLS].values
    y_raw = df[TARGET_COL].values

    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    class_names = le.classes_.tolist()

    save_model(le, "label_encoder")
    print(f"[train] Dataset: {len(df)} samples, {len(class_names)} classes")
    print(f"[train] Classes: {class_names}\n")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=seed, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=seed, stratify=y_train
    )

    print(f"[train] Split — train: {len(X_train)}, val: {len(X_val)}, test: {len(X_test)}")

    # ── Train & cross-validate each model ────────────────────────────────────
    models = build_models()
    cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=seed)

    results = {}
    for name, model in models.items():
        t0 = time.time()
        print(f"[train] Fitting {name}...")

        model.fit(X_train, y_train)

        cv_scores = cross_val_score(model, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
        val_acc = model.score(X_val, y_val)
        elapsed = time.time() - t0

        results[name] = {
            "cv_mean": float(cv_scores.mean()),
            "cv_std": float(cv_scores.std()),
            "val_accuracy": float(val_acc),
            "train_time_s": round(elapsed, 2),
        }

        save_model(model, name)
        print(
            f"         CV acc: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}  |  "
            f"val acc: {val_acc:.4f}  |  {elapsed:.1f}s"
        )

    # ── Select best model ─────────────────────────────────────────────────────
    best_name = max(results, key=lambda k: results[k]["val_accuracy"])
    print(f"\n[train] Best model: {best_name} (val acc = {results[best_name]['val_accuracy']:.4f})")

    # ── Persist metadata ──────────────────────────────────────────────────────
    metadata = {
        "best_model": best_name,
        "feature_cols": FEATURE_COLS,
        "class_names": class_names,
        "n_classes": len(class_names),
        "dataset_size": len(df),
        "split": {"train": len(X_train), "val": len(X_val), "test": len(X_test)},
        "cv_folds": cv_folds,
        "seed": seed,
        "trained_at": datetime.utcnow().isoformat(),
        "model_results": results,
    }
    save_json(metadata, "train_metadata.json")

    # Save test split for evaluate.py
    np.save(os.path.join(OUTPUTS_DIR, "X_test.npy"), X_test)
    np.save(os.path.join(OUTPUTS_DIR, "y_test.npy"), y_test)

    print(f"[train] Metadata saved → outputs/train_metadata.json")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=str, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--cv", type=int, default=5)
    args = parser.parse_args()
    train(data_path=args.data, seed=args.seed, cv_folds=args.cv)