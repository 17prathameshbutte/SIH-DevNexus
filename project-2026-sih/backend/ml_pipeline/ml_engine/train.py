"""
train.py
--------
Trains SmartScanScheduler on mock RF tensor inputs, using the same
DataLoader / train-val loop structure practiced in ANN_Regression.ipynb
and ANN_Classification.ipynb, adapted for a dual-head (regression +
classification) loss.

The 5-step core loop per batch:
    optimizer.zero_grad()
    outputs = model(inputs)
    loss = criterion(...)
    loss.backward()
    optimizer.step()

Saves trained weights to smart_scan_v1.pth
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from mock_rf_feed import generate_occupancy_tensor, NUM_CHANNELS, NUM_TIMESTEPS
from model import SmartScanScheduler

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
NUM_BANDS = NUM_CHANNELS          # discrete next-band choices = num channels
INPUT_DIM = NUM_CHANNELS * NUM_TIMESTEPS
EPOCHS = 100
BATCH_SIZE = 32
LR = 1e-3
WEIGHTS_PATH = "smart_scan_v1.pth"


def build_training_targets(occupancy_tensor, truth_tensor):
    """
    Derives supervised targets from the mock occupancy/truth tensors:
      - dwell_time target: proportion of "hot" timesteps per snapshot,
        scaled into a plausible dwell-time range (ms), simulating how long
        the scheduler should linger on that channel set.
      - band target: index of the channel with the highest transmission
        activity (i.e. the next best band to sweep).
    """
    B = occupancy_tensor.shape[0]

    activity_per_channel = truth_tensor.sum(dim=2)          # (B, C)
    band_targets = torch.argmax(activity_per_channel, dim=1).long()  # (B,)

    total_activity_ratio = truth_tensor.mean(dim=(1, 2))     # (B,)
    dwell_targets = (total_activity_ratio * 50.0 + 1.0).float().view(-1, 1)  # (B,1) ms

    return dwell_targets, band_targets


def get_dataloaders(n_train=800, n_val=200, seed=42):
    occ_train, truth_train = generate_occupancy_tensor(batch_size=n_train, seed=seed)
    occ_val, truth_val = generate_occupancy_tensor(batch_size=n_val, seed=seed + 1)

    X_train = occ_train.view(n_train, -1)
    X_val = occ_val.view(n_val, -1)

    dwell_train, band_train = build_training_targets(occ_train, truth_train)
    dwell_val, band_val = build_training_targets(occ_val, truth_val)

    train_dataset = TensorDataset(X_train, dwell_train, band_train)
    val_dataset = TensorDataset(X_val, dwell_val, band_val)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    return train_loader, val_loader


def train():
    train_loader, val_loader = get_dataloaders()

    model = SmartScanScheduler(input_dim=INPUT_DIM, num_bands=NUM_BANDS)

    dwell_criterion = nn.MSELoss()
    band_criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    train_losses = []
    val_losses = []
    best_val_loss = float("inf")

    for epoch in range(EPOCHS):
        model.train()
        running_loss = 0.0

        for xb, dwell_yb, band_yb in train_loader:
            # --- the 5-step core loop ---
            optimizer.zero_grad()
            dwell_pred, band_logits = model(xb)
            loss = dwell_criterion(dwell_pred, dwell_yb) + band_criterion(band_logits, band_yb)
            loss.backward()
            optimizer.step()
            # -----------------------------

            running_loss += loss.item()

        epoch_train_loss = running_loss / len(train_loader)
        train_losses.append(epoch_train_loss)

        # validation
        model.eval()
        running_val_loss = 0.0
        with torch.no_grad():
            for xb, dwell_yb, band_yb in val_loader:
                dwell_pred, band_logits = model(xb)
                loss = dwell_criterion(dwell_pred, dwell_yb) + band_criterion(band_logits, band_yb)
                running_val_loss += loss.item()

        epoch_val_loss = running_val_loss / len(val_loader)
        val_losses.append(epoch_val_loss)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"epoch {epoch+1}/{EPOCHS} ==> train loss = {epoch_train_loss:.4f} "
                  f"& val loss = {epoch_val_loss:.4f}")

        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            torch.save(model.state_dict(), WEIGHTS_PATH)

    print(f"\nTraining complete. Best val loss = {best_val_loss:.4f}")
    print(f"Weights saved to {WEIGHTS_PATH}")

    return model, train_losses, val_losses


if __name__ == "__main__":
    train()
