"""
evaluate.py
-----------
Loads the saved best model and runs a full evaluation suite on the held-out test set.

Metrics produced:
  - Accuracy, Balanced Accuracy
  - Precision / Recall / F1  (macro, weighted, per-class)
  - Cohen's Kappa
  - Matthews Correlation Coefficient (MCC)
  - ROC-AUC (macro OvR)
  - Log Loss
  - Top-2 / Top-3 Accuracy
  - Confusion matrix (normalised + raw)
  - Per-class calibration check (ECE)
  - SHAP feature importance (global + per-class)
  - Learning curve

Usage:
    python -m ml.evaluate
    python -m ml.evaluate --model xgboost
"""

import argparse
import json
import os
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    log_loss,
    matthews_corrcoef,
    roc_auc_score,
    top_k_accuracy_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import learning_curve, StratifiedKFold

import shap

from ml.utils import (
    FEATURE_COLS,
    OUTPUTS_DIR,
    load_model,
    save_json,
)

warnings.filterwarnings("ignore")

# ── Helpers ───────────────────────────────────────────────────────────────────

def savefig(name: str):
    path = os.path.join(OUTPUTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  → saved {path}")


def expected_calibration_error(y_true, y_prob, n_bins=10) -> float:
    """Compute ECE over all classes (one-vs-rest)."""
    n_classes = y_prob.shape[1]
    ece_vals = []
    for c in range(n_classes):
        binary = (y_true == c).astype(int)
        prob_c = y_prob[:, c]
        bin_edges = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
            mask = (prob_c >= lo) & (prob_c < hi)
            if mask.sum() == 0:
                continue
            acc = binary[mask].mean()
            conf = prob_c[mask].mean()
            ece += mask.sum() * abs(acc - conf)
        ece_vals.append(ece / len(y_true))
    return float(np.mean(ece_vals))


# ── Core evaluation ───────────────────────────────────────────────────────────

def evaluate(model_name: str | None = None) -> dict:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # Load metadata to find best model if not specified
    meta_path = os.path.join(OUTPUTS_DIR, "train_metadata.json")
    with open(meta_path) as f:
        meta = json.load(f)

    if model_name is None:
        model_name = meta["best_model"]

    class_names = meta["class_names"]
    print(f"[evaluate] Model: {model_name}")
    print(f"[evaluate] Classes: {len(class_names)}")

    model = load_model(model_name)
    le = load_model("label_encoder")

    X_test = np.load(os.path.join(OUTPUTS_DIR, "X_test.npy"))
    y_test = np.load(os.path.join(OUTPUTS_DIR, "y_test.npy"))

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)

    # ── Scalar metrics ─────────────────────────────────────────────────────────
    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)
    kappa = cohen_kappa_score(y_test, y_pred)
    mcc = matthews_corrcoef(y_test, y_pred)
    ll = log_loss(y_test, y_prob)
    roc_auc = roc_auc_score(y_test, y_prob, multi_class="ovr", average="macro")
    top2 = top_k_accuracy_score(y_test, y_prob, k=2)
    top3 = top_k_accuracy_score(y_test, y_prob, k=3)
    ece = expected_calibration_error(y_test, y_prob)

    prec_mac, rec_mac, f1_mac, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")
    prec_wt, rec_wt, f1_wt, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")
    prec_pc, rec_pc, f1_pc, sup_pc = precision_recall_fscore_support(y_test, y_pred, average=None)

    print(f"\n{'─'*50}")
    print(f"  Accuracy            : {acc:.4f}")
    print(f"  Balanced Accuracy   : {bal_acc:.4f}")
    print(f"  Cohen Kappa         : {kappa:.4f}")
    print(f"  MCC                 : {mcc:.4f}")
    print(f"  Log Loss            : {ll:.4f}")
    print(f"  ROC-AUC (macro OvR) : {roc_auc:.4f}")
    print(f"  Top-2 Accuracy      : {top2:.4f}")
    print(f"  Top-3 Accuracy      : {top3:.4f}")
    print(f"  ECE                 : {ece:.4f}")
    print(f"  F1 macro            : {f1_mac:.4f}")
    print(f"  F1 weighted         : {f1_wt:.4f}")
    print(f"{'─'*50}\n")

    # ── Per-class table ────────────────────────────────────────────────────────
    per_class = {}
    for i, crop in enumerate(class_names):
        per_class[crop] = {
            "precision": round(float(prec_pc[i]), 4),
            "recall": round(float(rec_pc[i]), 4),
            "f1": round(float(f1_pc[i]), 4),
            "support": int(sup_pc[i]),
        }

    metrics = {
        "model": model_name,
        "test_samples": int(len(y_test)),
        "accuracy": round(acc, 4),
        "balanced_accuracy": round(bal_acc, 4),
        "cohen_kappa": round(kappa, 4),
        "mcc": round(mcc, 4),
        "log_loss": round(ll, 4),
        "roc_auc_macro": round(roc_auc, 4),
        "top2_accuracy": round(top2, 4),
        "top3_accuracy": round(top3, 4),
        "ece": round(ece, 4),
        "f1_macro": round(f1_mac, 4),
        "f1_weighted": round(f1_wt, 4),
        "precision_macro": round(prec_mac, 4),
        "recall_macro": round(rec_mac, 4),
        "per_class": per_class,
    }
    save_json(metrics, "eval_metrics.json")

    # ── Plot 1: Confusion matrix (normalised) ─────────────────────────────────
    _plot_confusion_matrix(y_test, y_pred, class_names, normalise=True)
    _plot_confusion_matrix(y_test, y_pred, class_names, normalise=False)

    # ── Plot 2: Per-class F1 bar chart ─────────────────────────────────────────
    _plot_per_class_f1(class_names, f1_pc)

    # ── Plot 3: Feature importance ─────────────────────────────────────────────
    _plot_feature_importance(model, model_name)

    # ── Plot 4: SHAP summary ───────────────────────────────────────────────────
    _plot_shap(model, X_test, model_name)

    # ── Plot 5: Learning curve ─────────────────────────────────────────────────
    _plot_learning_curve(model, X_test, y_test)

    # ── Plot 6: Calibration curve ──────────────────────────────────────────────
    _plot_calibration(y_test, y_prob, class_names)

    # ── Plot 7: Model comparison bar chart (from train metadata) ──────────────
    _plot_model_comparison(meta)

    print("\n[evaluate] All outputs written to outputs/")
    return metrics


# ── Plot helpers ──────────────────────────────────────────────────────────────

def _plot_confusion_matrix(y_test, y_pred, class_names, normalise: bool):
    cm = confusion_matrix(y_test, y_pred)
    if normalise:
        cm_plot = cm.astype(float) / cm.sum(axis=1, keepdims=True)
        fmt, title, fname = ".2f", "Confusion matrix (normalised)", "confusion_matrix_norm.png"
    else:
        cm_plot = cm
        fmt, title, fname = "d", "Confusion matrix (raw counts)", "confusion_matrix_raw.png"

    n = len(class_names)
    fig_size = max(10, n * 0.55)
    fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.85))
    sns.heatmap(
        cm_plot, annot=True, fmt=fmt,
        xticklabels=class_names, yticklabels=class_names,
        cmap="Blues", linewidths=0.4, ax=ax,
    )
    ax.set_title(title, fontsize=13, pad=12)
    ax.set_xlabel("Predicted", fontsize=11)
    ax.set_ylabel("True", fontsize=11)
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", rotation=0)
    plt.tight_layout()
    savefig(fname)


def _plot_per_class_f1(class_names, f1_scores):
    sorted_idx = np.argsort(f1_scores)
    fig, ax = plt.subplots(figsize=(8, max(4, len(class_names) * 0.32)))
    bars = ax.barh(
        [class_names[i] for i in sorted_idx],
        [f1_scores[i] for i in sorted_idx],
        color=plt.cm.RdYlGn([f1_scores[i] for i in sorted_idx]),
        edgecolor="none",
        height=0.7,
    )
    ax.set_xlabel("F1 Score", fontsize=11)
    ax.set_title("Per-class F1 score", fontsize=13)
    ax.set_xlim(0, 1.05)
    for bar, idx in zip(bars, sorted_idx):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{f1_scores[idx]:.3f}", va="center", fontsize=8)
    plt.tight_layout()
    savefig("per_class_f1.png")


def _plot_feature_importance(model, model_name: str):
    # Handles both plain estimators and pipelines
    clf = model
    if hasattr(model, "named_steps"):
        clf = model.named_steps.get("clf", model)

    if not hasattr(clf, "feature_importances_"):
        print("  [skip] feature_importances_ not available for this model")
        return

    importances = clf.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(FEATURE_COLS)))
    ax.bar(
        [FEATURE_COLS[i] for i in sorted_idx],
        [importances[i] for i in sorted_idx],
        color=[colors[i] for i in sorted_idx],
        edgecolor="none",
    )
    ax.set_ylabel("Importance", fontsize=11)
    ax.set_title(f"Feature importance — {model_name}", fontsize=13)
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()
    savefig("feature_importance.png")


def _plot_shap(model, X_test, model_name: str):
    try:
        clf = model
        if hasattr(model, "named_steps"):
            clf = model.named_steps.get("clf", model)
            X_input = model.named_steps["scaler"].transform(X_test) if "scaler" in model.named_steps else X_test
        else:
            X_input = X_test

        if model_name in ("random_forest", "gradient_boosting", "xgboost"):
            explainer = shap.TreeExplainer(clf)
            sv = explainer.shap_values(X_input[:200])
            # sklearn RF returns ndarray of shape (n_samples, n_features, n_classes)
            # XGBoost / older SHAP returns list[n_classes] of (n_samples, n_features)
            if isinstance(sv, np.ndarray) and sv.ndim == 3:
                mean_abs = np.abs(sv).mean(axis=(0, 2))
            elif isinstance(sv, list):
                mean_abs = np.mean([np.abs(s) for s in sv], axis=0).mean(axis=0)
            else:
                mean_abs = np.abs(sv).mean(axis=0)
        else:
            explainer = shap.KernelExplainer(clf.predict_proba, shap.sample(X_input, 100))
            sv = explainer.shap_values(X_input[:50])
            mean_abs = np.mean([np.abs(s) for s in sv], axis=0).mean(axis=0)

        fig, ax = plt.subplots(figsize=(7, 4))
        mean_importance = mean_abs if mean_abs.ndim == 1 else mean_abs.mean(axis=0)
        sorted_idx = np.argsort(mean_importance)[::-1]
        ax.bar(
            [FEATURE_COLS[i] for i in sorted_idx],
            [mean_importance[i] for i in sorted_idx],
            color=plt.cm.plasma(np.linspace(0.2, 0.85, len(FEATURE_COLS))),
            edgecolor="none",
        )
        ax.set_ylabel("Mean |SHAP value|", fontsize=11)
        ax.set_title(f"SHAP global feature importance — {model_name}", fontsize=13)
        ax.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        savefig("shap_importance.png")
        print("  SHAP plot saved.")
    except Exception as e:
        print(f"  [skip] SHAP failed: {e}")


def _plot_learning_curve(model, X_test, y_test):
    # Learning curve needs training data; we re-load from saved split + test
    X_all = np.concatenate([X_test])  # minimal: just show test curve shape
    # Proper learning curve requires X_train — skip silently if unavailable
    try:
        X_train = np.load(os.path.join(OUTPUTS_DIR, "X_test.npy"))  # use test as proxy
        y_train = np.load(os.path.join(OUTPUTS_DIR, "y_test.npy"))

        train_sizes, train_scores, val_scores = learning_curve(
            model, X_train, y_train,
            cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
            train_sizes=np.linspace(0.1, 1.0, 8),
            scoring="accuracy",
            n_jobs=-1,
        )

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.fill_between(train_sizes, train_scores.mean(1) - train_scores.std(1),
                        train_scores.mean(1) + train_scores.std(1), alpha=0.15, color="#1f77b4")
        ax.fill_between(train_sizes, val_scores.mean(1) - val_scores.std(1),
                        val_scores.mean(1) + val_scores.std(1), alpha=0.15, color="#ff7f0e")
        ax.plot(train_sizes, train_scores.mean(1), "o-", label="Train", color="#1f77b4")
        ax.plot(train_sizes, val_scores.mean(1), "s-", label="Validation", color="#ff7f0e")
        ax.set_xlabel("Training samples", fontsize=11)
        ax.set_ylabel("Accuracy", fontsize=11)
        ax.set_title("Learning curve", fontsize=13)
        ax.legend()
        ax.set_ylim(0, 1.05)
        plt.tight_layout()
        savefig("learning_curve.png")
    except Exception as e:
        print(f"  [skip] Learning curve: {e}")


def _plot_calibration(y_test, y_prob, class_names):
    # Show calibration for first 6 classes to keep plot readable
    fig, axes = plt.subplots(2, 3, figsize=(12, 7))
    axes = axes.flatten()
    for i, (ax, crop) in enumerate(zip(axes, class_names[:6])):
        binary = (y_test == i).astype(int)
        prob_c = y_prob[:, i]
        if binary.sum() == 0:
            ax.axis("off")
            continue
        try:
            frac_pos, mean_pred = calibration_curve(binary, prob_c, n_bins=8)
            ax.plot([0, 1], [0, 1], "k--", lw=0.8, label="Perfect")
            ax.plot(mean_pred, frac_pos, "s-", color="#1f77b4", ms=5, label=crop)
            ax.set_title(crop, fontsize=9)
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            ax.tick_params(labelsize=7)
        except Exception:
            ax.axis("off")
    fig.suptitle("Calibration curves (first 6 classes)", fontsize=13)
    plt.tight_layout()
    savefig("calibration_curves.png")


def _plot_model_comparison(meta: dict):
    results = meta.get("model_results", {})
    if not results:
        return

    names = list(results.keys())
    cv_means = [results[n]["cv_mean"] for n in names]
    val_accs = [results[n]["val_accuracy"] for n in names]

    x = np.arange(len(names))
    w = 0.35
    fig, ax = plt.subplots(figsize=(9, 4.5))
    b1 = ax.bar(x - w / 2, cv_means, w, label="CV mean accuracy", color="#4C72B0", edgecolor="none")
    b2 = ax.bar(x + w / 2, val_accs, w, label="Val accuracy", color="#DD8452", edgecolor="none")
    ax.set_xticks(x)
    ax.set_xticklabels([n.replace("_", "\n") for n in names], fontsize=9)
    ax.set_ylabel("Accuracy", fontsize=11)
    ax.set_title("Model comparison — CV vs val accuracy", fontsize=13)
    ax.set_ylim(0, 1.1)
    ax.legend()
    for bar in list(b1) + list(b2):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                f"{bar.get_height():.3f}", ha="center", va="bottom", fontsize=7.5)
    plt.tight_layout()
    savefig("model_comparison.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default=None, help="Model name to evaluate (default: best)")
    args = parser.parse_args()
    evaluate(model_name=args.model)