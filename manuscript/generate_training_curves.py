#!/usr/bin/env python3
"""
Generate VQC training curves (train vs validation loss) for Figure 7.

This script trains the VQC with an 80/20 train-validation split and
records per-epoch MSE on both sets, producing the empirical evidence
of overfitting that the reviewer requested.

Run from project root:
  .venv/bin/python manuscript/generate_training_curves.py

Runtime: ~30-45 minutes (2 properties × 80 epochs × 111 substances)
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pennylane as qml
import pennylane.numpy as pnp

from backend.quantum_predictor import (
    extract_features, quantum_circuit, circuit_predict,
    N_QUBITS, N_LAYERS, FEATURE_NAMES
)
from backend.spin_database import SUBSTANCES

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "backend", ".qml_cache")
HISTORY_FILE = os.path.join(CACHE_DIR, "training_history.json")
FIGDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")


def train_with_history(features_list, targets, n_epochs=80, lr=0.04,
                       val_features=None, val_targets=None, label=""):
    """
    Train VQC and record per-epoch train and validation MSE.

    Returns: (weights, readout_weights, train_history, val_history)
    """
    np.random.seed(42)
    weights = pnp.array(
        np.random.uniform(-0.5, 0.5, (N_LAYERS, N_QUBITS, 3)),
        requires_grad=True
    )
    readout_weights = pnp.array(
        np.random.uniform(-0.5, 0.5, N_QUBITS + 1),
        requires_grad=True
    )

    opt = qml.AdamOptimizer(stepsize=lr)

    def cost_fn(weights, readout_weights):
        total_loss = pnp.array(0.0)
        for feat, target in zip(features_list, targets):
            pred = circuit_predict(feat, weights, readout_weights)
            total_loss = total_loss + (pred - target) ** 2
        return total_loss / len(features_list)

    def eval_mse(feats, tgts, w, rw):
        """Evaluate MSE without gradients."""
        total = 0.0
        for feat, target in zip(feats, tgts):
            pred = float(circuit_predict(feat, w, rw))
            total += (pred - float(target)) ** 2
        return total / len(feats)

    train_history = []
    val_history = []

    t0 = time.time()
    for epoch in range(n_epochs):
        (weights, readout_weights), loss = opt.step_and_cost(
            cost_fn, weights, readout_weights
        )

        train_mse = float(loss)
        train_history.append(train_mse)

        if val_features is not None:
            val_mse = eval_mse(val_features, val_targets, weights, readout_weights)
            val_history.append(val_mse)
            val_str = f", Val MSE = {val_mse:.4f}"
        else:
            val_str = ""

        elapsed = time.time() - t0
        eta = elapsed / (epoch + 1) * (n_epochs - epoch - 1)
        if epoch % 5 == 0 or epoch == n_epochs - 1:
            print(f"  [{label}] Epoch {epoch:3d}/{n_epochs}: "
                  f"Train MSE = {train_mse:.4f}{val_str} "
                  f"({elapsed:.0f}s elapsed, ~{eta:.0f}s remaining)")

    return weights, readout_weights, train_history, val_history


def main():
    # Check cache first
    if os.path.exists(HISTORY_FILE):
        print(f"Training history already cached at {HISTORY_FILE}")
        print("Delete it to re-generate. Skipping training.")
        plot_from_cache()
        return

    print("Generating VQC training curves...\n")

    # Prepare data
    all_features = [extract_features(sub) for sub in SUBSTANCES]
    all_deg = [pnp.array(np.log10(max(s["degT50_soil"], 0.1)), requires_grad=False)
               for s in SUBSTANCES]
    all_koc = [pnp.array(np.log10(max(s["koc"], 0.1)), requires_grad=False)
               for s in SUBSTANCES]

    n = len(SUBSTANCES)

    # 80/20 train-validation split (reproducible)
    rng = np.random.RandomState(42)
    indices = rng.permutation(n)
    n_train = int(0.8 * n)  # 88 train, 23 val
    train_idx = indices[:n_train]
    val_idx = indices[n_train:]
    print(f"Split: {n_train} train, {n - n_train} validation\n")

    train_feat = [all_features[i] for i in train_idx]
    val_feat = [all_features[i] for i in val_idx]

    # ── DegT50 ──
    train_deg = [all_deg[i] for i in train_idx]
    val_deg = [all_deg[i] for i in val_idx]

    print("── Training DegT50 model ──")
    _, _, deg_train_h, deg_val_h = train_with_history(
        train_feat, train_deg, n_epochs=80, lr=0.04,
        val_features=val_feat, val_targets=val_deg, label="DegT50"
    )

    # ── Koc ──
    train_koc = [all_koc[i] for i in train_idx]
    val_koc = [all_koc[i] for i in val_idx]

    print("\n── Training Koc model ──")
    _, _, koc_train_h, koc_val_h = train_with_history(
        train_feat, train_koc, n_epochs=80, lr=0.04,
        val_features=val_feat, val_targets=val_koc, label="Koc"
    )

    # Save history
    history = {
        "n_train": n_train,
        "n_val": n - n_train,
        "n_epochs": 80,
        "deg_train": deg_train_h,
        "deg_val": deg_val_h,
        "koc_train": koc_train_h,
        "koc_val": koc_val_h,
    }

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    print(f"\n✓ Training history saved to {HISTORY_FILE}")

    # Generate figure
    plot_training_curves(history)


def plot_from_cache():
    with open(HISTORY_FILE) as f:
        history = json.load(f)
    plot_training_curves(history)


def plot_training_curves(history):
    """Generate Figure 7: Training curves."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    rcParams.update({
        "font.family": "serif",
        "font.size": 9,
        "axes.labelsize": 10,
        "axes.titlesize": 10,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
    })

    epochs = np.arange(1, len(history["deg_train"]) + 1)

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.8))

    # DegT50
    ax = axes[0]
    ax.plot(epochs, history["deg_train"], "-", color="#2563eb", lw=1.2,
            label=f"Train (n={history['n_train']})")
    ax.plot(epochs, history["deg_val"], "--", color="#dc2626", lw=1.2,
            label=f"Validation (n={history['n_val']})")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE (log$_{10}$ scale)")
    ax.set_title("(a) DegT50 — VQC training curves", fontsize=9)
    ax.legend(frameon=False)
    ax.set_xlim(0, len(epochs))

    # Annotate divergence
    min_val_epoch = np.argmin(history["deg_val"]) + 1
    min_val = min(history["deg_val"])
    ax.axvline(min_val_epoch, color="#9ca3af", ls=":", lw=0.8, alpha=0.7)
    ax.annotate(f"Best val epoch {min_val_epoch}",
                xy=(min_val_epoch, min_val), fontsize=6.5,
                xytext=(min_val_epoch + 8, min_val + 0.05),
                arrowprops=dict(arrowstyle="->", color="#9ca3af", lw=0.8),
                color="#6b7280")

    # Koc
    ax = axes[1]
    ax.plot(epochs, history["koc_train"], "-", color="#059669", lw=1.2,
            label=f"Train (n={history['n_train']})")
    ax.plot(epochs, history["koc_val"], "--", color="#dc2626", lw=1.2,
            label=f"Validation (n={history['n_val']})")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE (log$_{10}$ scale)")
    ax.set_title("(b) K$_{oc}$ — VQC training curves", fontsize=9)
    ax.legend(frameon=False)
    ax.set_xlim(0, len(epochs))

    min_val_epoch = np.argmin(history["koc_val"]) + 1
    min_val = min(history["koc_val"])
    ax.axvline(min_val_epoch, color="#9ca3af", ls=":", lw=0.8, alpha=0.7)
    ax.annotate(f"Best val epoch {min_val_epoch}",
                xy=(min_val_epoch, min_val), fontsize=6.5,
                xytext=(min_val_epoch + 8, min_val + 0.05),
                arrowprops=dict(arrowstyle="->", color="#9ca3af", lw=0.8),
                color="#6b7280")

    plt.tight_layout()
    os.makedirs(FIGDIR, exist_ok=True)
    plt.savefig(os.path.join(FIGDIR, "fig7_training_curves.pdf"))
    plt.savefig(os.path.join(FIGDIR, "fig7_training_curves.png"))
    plt.close()
    print(f"✓ Figure 7 saved to {FIGDIR}/fig7_training_curves.pdf")


if __name__ == "__main__":
    main()
