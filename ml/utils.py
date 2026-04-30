import os
import json
import joblib
import numpy as np
import pandas as pd

FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COL = "label"

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_data(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = os.path.join(DATA_DIR, "crop_recommendation.csv")
    df = pd.read_csv(path)
    assert all(c in df.columns for c in FEATURE_COLS + [TARGET_COL]), (
        f"CSV missing expected columns. Found: {df.columns.tolist()}"
    )
    return df


def save_model(model, name: str) -> str:
    os.makedirs(MODELS_DIR, exist_ok=True)
    path = os.path.join(MODELS_DIR, f"{name}.joblib")
    joblib.dump(model, path)
    return path


def load_model(name: str):
    path = os.path.join(MODELS_DIR, f"{name}.joblib")
    return joblib.load(path)


def save_json(data: dict, filename: str) -> str:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    path = os.path.join(OUTPUTS_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path


def set_seed(seed: int = 42):
    np.random.seed(seed)