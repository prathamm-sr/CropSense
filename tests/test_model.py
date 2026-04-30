"""
tests/test_model.py
-------------------
pytest suite for the ML pipeline.

Run with:
    pytest tests/ -v
    pytest tests/ -v --tb=short
"""

import json
import os

import numpy as np
import pytest

from ml.utils import FEATURE_COLS, OUTPUTS_DIR

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def predictor():
    from ml.predict import Predictor
    return Predictor()


@pytest.fixture(scope="module")
def eval_metrics():
    path = os.path.join(OUTPUTS_DIR, "eval_metrics.json")
    with open(path) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def train_metadata():
    path = os.path.join(OUTPUTS_DIR, "train_metadata.json")
    with open(path) as f:
        return json.load(f)


VALID_SAMPLE = {
    "N": 90, "P": 42, "K": 43,
    "temperature": 20.87, "humidity": 82.0,
    "ph": 6.5, "rainfall": 202.9,
}

# ── Smoke tests ───────────────────────────────────────────────────────────────

class TestPredictor:
    def test_predict_returns_result(self, predictor):
        result = predictor.predict(VALID_SAMPLE)
        assert result.top_crop is not None
        assert isinstance(result.top_crop, str)

    def test_confidence_in_unit_range(self, predictor):
        result = predictor.predict(VALID_SAMPLE)
        assert 0.0 <= result.confidence <= 1.0

    def test_top_k_length(self, predictor):
        result = predictor.predict(VALID_SAMPLE, top_k=3)
        assert len(result.top_k) == 3

    def test_top_k_probabilities_sum_leq_one(self, predictor):
        result = predictor.predict(VALID_SAMPLE, top_k=5)
        total = sum(item["probability"] for item in result.top_k)
        assert total <= 1.001  # small float tolerance

    def test_top_k_sorted_descending(self, predictor):
        result = predictor.predict(VALID_SAMPLE, top_k=5)
        probs = [item["probability"] for item in result.top_k]
        assert probs == sorted(probs, reverse=True)

    def test_output_contains_all_input_features(self, predictor):
        result = predictor.predict(VALID_SAMPLE)
        for feat in FEATURE_COLS:
            assert feat in result.input_features

    def test_to_dict_is_serialisable(self, predictor):
        result = predictor.predict(VALID_SAMPLE)
        d = result.to_dict()
        assert isinstance(d, dict)
        import json
        json.dumps(d)  # must not raise

    def test_missing_feature_raises(self, predictor):
        bad = {k: v for k, v in VALID_SAMPLE.items() if k != "ph"}
        with pytest.raises(ValueError, match="Missing features"):
            predictor.predict(bad)

    def test_out_of_range_feature_raises(self, predictor):
        bad = {**VALID_SAMPLE, "ph": 99.0}
        with pytest.raises(ValueError, match="outside expected range"):
            predictor.predict(bad)

    def test_deterministic_output(self, predictor):
        r1 = predictor.predict(VALID_SAMPLE)
        r2 = predictor.predict(VALID_SAMPLE)
        assert r1.top_crop == r2.top_crop
        assert r1.confidence == r2.confidence

    def test_known_sample_rice(self, predictor):
        """Soil conditions that strongly favour rice."""
        rice_conditions = {
            "N": 60, "P": 55, "K": 44,
            "temperature": 23.0, "humidity": 82.0,
            "ph": 6.0, "rainfall": 230.0,
        }
        result = predictor.predict(rice_conditions)
        top_crops = [item["crop"] for item in result.top_k[:3]]
        assert "rice" in top_crops, f"Expected rice in top-3, got {top_crops}"

    def test_known_sample_cotton(self, predictor):
        """Soil conditions that strongly favour cotton."""
        cotton_conditions = {
            "N": 117, "P": 46, "K": 20,
            "temperature": 24.0, "humidity": 80.0,
            "ph": 6.5, "rainfall": 70.0,
        }
        result = predictor.predict(cotton_conditions)
        top_crops = [item["crop"] for item in result.top_k[:3]]
        assert "cotton" in top_crops, f"Expected cotton in top-3, got {top_crops}"


# ── Metric threshold tests ────────────────────────────────────────────────────

class TestMetricThresholds:
    """Hard quality gates — CI will fail if model degrades below these."""

    def test_accuracy_above_threshold(self, eval_metrics):
        assert eval_metrics["accuracy"] >= 0.95, (
            f"Accuracy {eval_metrics['accuracy']} below 0.95 threshold"
        )

    def test_balanced_accuracy_above_threshold(self, eval_metrics):
        assert eval_metrics["balanced_accuracy"] >= 0.95

    def test_f1_macro_above_threshold(self, eval_metrics):
        assert eval_metrics["f1_macro"] >= 0.95

    def test_roc_auc_above_threshold(self, eval_metrics):
        assert eval_metrics["roc_auc_macro"] >= 0.99

    def test_log_loss_below_threshold(self, eval_metrics):
        assert eval_metrics["log_loss"] <= 0.25, (
            f"Log loss {eval_metrics['log_loss']} above 0.25 threshold"
        )

    def test_mcc_above_threshold(self, eval_metrics):
        assert eval_metrics["mcc"] >= 0.95

    def test_kappa_above_threshold(self, eval_metrics):
        assert eval_metrics["cohen_kappa"] >= 0.95

    def test_no_class_f1_below_floor(self, eval_metrics):
        """No individual crop should drop below 0.80 F1."""
        for crop, stats in eval_metrics["per_class"].items():
            assert stats["f1"] >= 0.80, (
                f"Class '{crop}' F1 = {stats['f1']} is below 0.80 floor"
            )

    def test_top2_accuracy_near_perfect(self, eval_metrics):
        assert eval_metrics["top2_accuracy"] >= 0.99

    def test_ece_reasonable(self, eval_metrics):
        assert eval_metrics["ece"] <= 0.10, (
            f"ECE {eval_metrics['ece']} above 0.10 — model may be poorly calibrated"
        )


# ── Metadata integrity tests ──────────────────────────────────────────────────

class TestMetadata:
    def test_metadata_has_required_keys(self, train_metadata):
        required = ["best_model", "feature_cols", "class_names", "split", "model_results"]
        for key in required:
            assert key in train_metadata, f"Missing key: {key}"

    def test_feature_cols_unchanged(self, train_metadata):
        assert train_metadata["feature_cols"] == FEATURE_COLS

    def test_22_classes_present(self, train_metadata):
        assert train_metadata["n_classes"] == 22

    def test_all_models_trained(self, train_metadata):
        expected = {"random_forest", "xgboost", "gradient_boosting",
                    "logistic_regression", "svm"}
        trained = set(train_metadata["model_results"].keys())
        assert expected == trained

    def test_split_sizes_nonzero(self, train_metadata):
        for split_name, size in train_metadata["split"].items():
            assert size > 0, f"Split '{split_name}' has size 0"