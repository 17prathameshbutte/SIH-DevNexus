"""
model.py
--------
SmartScanScheduler: a dual-head PyTorch network that ingests a channel
occupancy feature vector and predicts:

  Head 1 (regression)     -> next dwell time  (delta_t_dwell), continuous
  Head 2 (classification) -> next sweep band index (f_next), discrete

Architecture follows the same nn.Sequential / nn.Module style practiced in
ANN_Regression.ipynb and ANN_Classification.ipynb, split into a shared
trunk + two output heads.
"""

import torch
import torch.nn as nn


class SmartScanScheduler(nn.Module):
    def __init__(self, input_dim, num_bands, hidden_dims=(128, 64)):
        """
        input_dim : size of the flattened channel-occupancy input vector
        num_bands : number of discrete frequency bands the scheduler can
                    choose to sweep next (classification head output size)
        """
        super(SmartScanScheduler, self).__init__()

        h1, h2 = hidden_dims

        # shared trunk
        self.trunk = nn.Sequential(
            nn.Linear(input_dim, h1),
            nn.ReLU(),
            nn.Linear(h1, h2),
            nn.ReLU(),
        )

        # Head 1: continuous dwell time prediction (regression)
        self.dwell_head = nn.Linear(h2, 1)

        # Head 2: discrete next sweep band index (classification)
        self.band_head = nn.Linear(h2, num_bands)

    def forward(self, x):
        shared = self.trunk(x)

        dwell_time = self.dwell_head(shared)   # (batch, 1)
        band_logits = self.band_head(shared)   # (batch, num_bands)

        return dwell_time, band_logits


if __name__ == "__main__":
    # quick shape sanity check
    torch.manual_seed(42)

    batch_size = 4
    input_dim = 10 * 50   # flattened (C=10, T=50) occupancy tensor
    num_bands = 10

    model = SmartScanScheduler(input_dim=input_dim, num_bands=num_bands)
    dummy_input = torch.randn(batch_size, input_dim)

    dwell_out, band_out = model(dummy_input)
    print("dwell_time output shape:", dwell_out.shape)   # (4, 1)
    print("band_logits output shape:", band_out.shape)   # (4, 10)
