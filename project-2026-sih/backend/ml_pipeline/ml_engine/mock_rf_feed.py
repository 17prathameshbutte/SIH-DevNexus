"""
mock_rf_feed.py
----------------
Generates a mock RF spectrum tensor to locally simulate the channel-occupancy
feed that would normally come from the receiver front-end.

Shape convention:  (B, C, T)
    B -> batch size          (number of independent scan snapshots)
    C -> frequency channels  (10 simulated channels)
    T -> time steps          (50 time steps per snapshot)

Each cell holds a simulated "energy" reading for that channel at that
time-step, plus a handful of derived PDW-style scalar features
(Center Frequency, Pulse Width, Amplitude, AoA) attached per channel so
downstream preprocessing.py has something realistic to scale.
"""

import numpy as np
import torch

# ---- simulation constants -------------------------------------------------
NUM_CHANNELS = 10      # C : frequency channels covered by own receiver
NUM_TIMESTEPS = 50     # T : scan time-steps per snapshot
DEFAULT_BATCH = 16     # B : number of snapshots per mock batch

FREQ_BAND_MHZ = (2000.0, 18000.0)   # center-frequency range (2-18 GHz)
PULSE_WIDTH_US = (0.1, 50.0)        # pulse width range in microseconds
AMPLITUDE_DBM = (-90.0, -10.0)      # received amplitude range
AOA_DEG = (0.0, 360.0)              # angle of arrival range


def generate_occupancy_tensor(batch_size=DEFAULT_BATCH,
                               num_channels=NUM_CHANNELS,
                               num_timesteps=NUM_TIMESTEPS,
                               p_transmission=0.15,
                               seed=None):
    """
    Returns a (B, C, T) float tensor of simulated channel occupancy energy,
    and a (B, C, T) binary truth tensor (1 = transmission present).
    """
    rng = np.random.default_rng(seed)

    # ground truth: is a channel "hot" (transmitting) at each timestep
    truth = rng.binomial(1, p_transmission, size=(batch_size, num_channels, num_timesteps))

    # baseline thermal noise floor + spikes where truth == 1
    noise_floor = rng.normal(loc=-95.0, scale=3.0,
                              size=(batch_size, num_channels, num_timesteps))
    signal_energy = rng.normal(loc=-30.0, scale=8.0,
                                size=(batch_size, num_channels, num_timesteps))

    occupancy = np.where(truth == 1, signal_energy, noise_floor)

    occupancy_tensor = torch.tensor(occupancy, dtype=torch.float32)
    truth_tensor = torch.tensor(truth, dtype=torch.float32)

    return occupancy_tensor, truth_tensor


def generate_pdw_batch(n_samples=500, seed=None):
    """
    Generates a flat (n_samples, 4) array of raw PDW-style scalar features:
    [Center Frequency (fc), Pulse Width (PW), Amplitude, Angle of Arrival (AoA)]
    Useful as the "raw RF variables" input expected by preprocessing.py.
    """
    rng = np.random.default_rng(seed)

    fc = rng.uniform(*FREQ_BAND_MHZ, size=n_samples)
    pw = rng.uniform(*PULSE_WIDTH_US, size=n_samples)
    amp = rng.uniform(*AMPLITUDE_DBM, size=n_samples)
    aoa = rng.uniform(*AOA_DEG, size=n_samples)

    pdw = np.stack([fc, pw, amp, aoa], axis=1)
    return pdw


if __name__ == "__main__":
    occ, truth = generate_occupancy_tensor(seed=42)
    print("occupancy tensor shape (B, C, T):", occ.shape)
    print("truth tensor shape      (B, C, T):", truth.shape)
    print("sample occupancy slice [0, :, :5]:\n", occ[0, :, :5])

    pdw = generate_pdw_batch(n_samples=5, seed=42)
    print("\nsample raw PDW rows [fc, PW, Amplitude, AoA]:\n", pdw)
