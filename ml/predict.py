"""
predict.py
----------
Clean inference interface. Loads the best saved model and label encoder,
accepts a dict or DataFrame of soil parameters, returns top-k predictions
with confidence scores.

Usage (CLI):
    python -m ml.predict --N 90 --P 42 --K 43 --temperature 20.8 \
                         --humidity 82.0 --ph 6.5 --rainfall 202.9

Usage (programmatic):
    from ml.predict import Predictor
    p = Predictor()
    result = p.predict({"N": 90, "P": 42, "K": 43,
                        "temperature": 20.8, "humidity": 82.0,
                        "ph": 6.5, "rainfall": 202.9})
"""

import argparse
import json
import os
from dataclasses import dataclass, asdict

import numpy as np

from ml.utils import FEATURE_COLS, OUTPUTS_DIR, load_model


# ── Value ranges for input validation (based on dataset statistics) ───────────
FEATURE_RANGES = {
    "N":           (0,   140),
    "P":           (5,   145),
    "K":           (5,   205),
    "temperature": (8.0,  44.0),
    "humidity":    (14.0, 100.0),
    "ph":          (3.5,  9.5),
    "rainfall":    (20.0, 300.0),
}


@dataclass
class PredictionResult:
    top_crop: str
    confidence: float            # probability of top prediction
    top_k: list[dict]            # list of {crop, probability} sorted desc
    input_features: dict
    model_used: str

    def to_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        lines = [
            f"  Recommended crop : {self.top_crop}",
            f"  Confidence       : {self.confidence:.1%}",
            f"  Model            : {self.model_used}",
            "",
            "  Top predictions:",
        ]
        for i, item in enumerate(self.top_k, 1):
            lines.append(f"    {i}. {item['crop']:<20} {item['probability']:.1%}")
        return "\n".join(lines)


class Predictor:
    def __init__(self, model_name: str | None = None):
        meta_path = os.path.join(OUTPUTS_DIR, "train_metadata.json")
        with open(meta_path) as f:
            meta = json.load(f)

        self.model_name = model_name or meta["best_model"]
        self.class_names = meta["class_names"]
        self.model = load_model(self.model_name)
        self.le = load_model("label_encoder")

    def _validate(self, features: dict) -> np.ndarray:
        missing = [f for f in FEATURE_COLS if f not in features]
        if missing:
            raise ValueError(f"Missing features: {missing}")

        for feat, val in features.items():
            if feat not in FEATURE_RANGES:
                continue
            lo, hi = FEATURE_RANGES[feat]
            if not (lo <= float(val) <= hi):
                raise ValueError(
                    f"Feature '{feat}' = {val} is outside expected range [{lo}, {hi}]"
                )

        return np.array([[float(features[f]) for f in FEATURE_COLS]])

    def predict(self, features: dict, top_k: int = 5) -> PredictionResult:
        X = self._validate(features)
        proba = self.model.predict_proba(X)[0]

        sorted_idx = np.argsort(proba)[::-1]
        top_k_list = [
            {"crop": self.class_names[i], "probability": round(float(proba[i]), 4)}
            for i in sorted_idx[:top_k]
        ]

        return PredictionResult(
            top_crop=top_k_list[0]["crop"],
            confidence=round(float(top_k_list[0]["probability"]), 4),
            top_k=top_k_list,
            input_features={k: float(v) for k, v in features.items() if k in FEATURE_COLS},
            model_used=self.model_name,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Predict the best crop given soil parameters.")
    for feat in FEATURE_COLS:
        parser.add_argument(f"--{feat}", type=float, required=True)
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--top_k", type=int, default=5)
    args = parser.parse_args()

    features = {f: getattr(args, f) for f in FEATURE_COLS}
    predictor = Predictor(model_name=args.model)
    result = predictor.predict(features, top_k=args.top_k)
    print(result)