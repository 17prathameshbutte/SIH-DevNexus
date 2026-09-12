"""Generate a realistic synthetic HDF5 radar emitter dataset for SmartScan-EW demo."""
import h5py
import numpy as np
import os
import sys

def generate(output_path: str = None):
    if output_path is None:
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'dataset.h5')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rng = np.random.default_rng(42)

    # Define transmitter parameters
    transmitters = [
        # Periodic emitters (stable frequency, regular PRI)
        {"id": 1,  "freq": 2500,  "bw": 10, "pri": 1000, "pri_jitter": 0.02, "pw": 5.0,  "pw_jitter": 0.05, "pos": [25.0, 40.0, 0.0],   "peak_pwr": 60, "avg_pwr": 55, "type": "periodic",         "scan_rate": 6.0,  "sector": 360},
        {"id": 2,  "freq": 3200,  "bw": 15, "pri": 800,  "pri_jitter": 0.01, "pw": 3.0,  "pw_jitter": 0.03, "pos": [30.0, 35.0, 100.0], "peak_pwr": 55, "avg_pwr": 50, "type": "periodic",         "scan_rate": 12.0, "sector": 360},
        {"id": 3,  "freq": 5800,  "bw": 20, "pri": 2000, "pri_jitter": 0.03, "pw": 10.0, "pw_jitter": 0.04, "pos": [20.0, 45.0, 50.0],  "peak_pwr": 65, "avg_pwr": 60, "type": "periodic",         "scan_rate": 3.0,  "sector": 180},
        {"id": 4,  "freq": 9400,  "bw": 25, "pri": 500,  "pri_jitter": 0.01, "pw": 1.5,  "pw_jitter": 0.02, "pos": [35.0, 30.0, 200.0], "peak_pwr": 70, "avg_pwr": 65, "type": "periodic",         "scan_rate": 15.0, "sector": 360},
        {"id": 5,  "freq": 15000, "bw": 30, "pri": 3000, "pri_jitter": 0.02, "pw": 8.0,  "pw_jitter": 0.03, "pos": [28.0, 38.0, 0.0],   "peak_pwr": 50, "avg_pwr": 45, "type": "periodic",         "scan_rate": 4.0,  "sector": 90},
        # Frequency-agile emitters (hop between frequencies)
        {"id": 6,  "freq": 4000,  "bw": 200,"pri": 1500, "pri_jitter": 0.05, "pw": 4.0,  "pw_jitter": 0.06, "pos": [22.0, 42.0, 150.0], "peak_pwr": 58, "avg_pwr": 53, "type": "frequency_agile",  "scan_rate": 8.0,  "sector": 360, "hop_freqs": [3800, 4000, 4200, 4400]},
        {"id": 7,  "freq": 6500,  "bw": 150,"pri": 700,  "pri_jitter": 0.04, "pw": 2.5,  "pw_jitter": 0.05, "pos": [32.0, 36.0, 80.0],  "peak_pwr": 62, "avg_pwr": 57, "type": "frequency_agile",  "scan_rate": 10.0, "sector": 270, "hop_freqs": [6200, 6500, 6800]},
        {"id": 8,  "freq": 8200,  "bw": 180,"pri": 1200, "pri_jitter": 0.03, "pw": 6.0,  "pw_jitter": 0.04, "pos": [26.0, 44.0, 120.0], "peak_pwr": 56, "avg_pwr": 51, "type": "frequency_agile",  "scan_rate": 5.0,  "sector": 360, "hop_freqs": [7800, 8000, 8200, 8400, 8600]},
        {"id": 9,  "freq": 11000, "bw": 250,"pri": 900,  "pri_jitter": 0.06, "pw": 3.5,  "pw_jitter": 0.07, "pos": [33.0, 33.0, 90.0],  "peak_pwr": 64, "avg_pwr": 59, "type": "frequency_agile",  "scan_rate": 7.0,  "sector": 180, "hop_freqs": [10500, 11000, 11500]},
        # Intermittent emitters (on/off with varying duty cycles)
        {"id": 10, "freq": 3600,  "bw": 12, "pri": 2500, "pri_jitter": 0.02, "pw": 7.0,  "pw_jitter": 0.03, "pos": [24.0, 41.0, 60.0],  "peak_pwr": 52, "avg_pwr": 47, "type": "intermittent",     "scan_rate": 4.0,  "sector": 360, "on_sec": 2.0, "off_sec": 5.0},
        {"id": 11, "freq": 7200,  "bw": 18, "pri": 1800, "pri_jitter": 0.03, "pw": 5.5,  "pw_jitter": 0.04, "pos": [29.0, 37.0, 40.0],  "peak_pwr": 57, "avg_pwr": 52, "type": "intermittent",     "scan_rate": 6.0,  "sector": 270, "on_sec": 3.0, "off_sec": 4.0},
        {"id": 12, "freq": 13500, "bw": 22, "pri": 4000, "pri_jitter": 0.04, "pw": 12.0, "pw_jitter": 0.05, "pos": [31.0, 34.0, 180.0], "peak_pwr": 48, "avg_pwr": 43, "type": "intermittent",     "scan_rate": 2.0,  "sector": 90,  "on_sec": 1.5, "off_sec": 8.0},
        # Mixed / additional
        {"id": 13, "freq": 5200,  "bw": 16, "pri": 600,  "pri_jitter": 0.02, "pw": 2.0,  "pw_jitter": 0.03, "pos": [27.0, 39.0, 110.0], "peak_pwr": 66, "avg_pwr": 61, "type": "periodic",         "scan_rate": 20.0, "sector": 360},
        {"id": 14, "freq": 10200, "bw": 200,"pri": 1100, "pri_jitter": 0.05, "pw": 4.5,  "pw_jitter": 0.06, "pos": [34.0, 32.0, 70.0],  "peak_pwr": 59, "avg_pwr": 54, "type": "frequency_agile",  "scan_rate": 9.0,  "sector": 360, "hop_freqs": [9800, 10000, 10200, 10400]},
        {"id": 15, "freq": 16500, "bw": 14, "pri": 3500, "pri_jitter": 0.03, "pw": 9.0,  "pw_jitter": 0.04, "pos": [23.0, 43.0, 30.0],  "peak_pwr": 45, "avg_pwr": 40, "type": "intermittent",     "scan_rate": 3.0,  "sector": 180, "on_sec": 4.0, "off_sec": 6.0},
    ]

    sim_duration_sec = 60.0
    dt = 0.0001  # 100 microsecond time resolution for pulse generation

    with h5py.File(output_path, 'w') as f:
        # --- Simulation Info ---
        meta = f.create_group('metadata')
        sim_info = meta.create_group('simulation_info')
        sim_info.attrs['version'] = '1.0'
        sim_info.attrs['created_date'] = '2026-08-26'
        sim_info.attrs['description'] = 'Synthetic EW radar emitter dataset for SmartScan-EW prototype'
        sim_info.attrs['duration_sec'] = sim_duration_sec
        sim_info.attrs['num_transmitters'] = len(transmitters)

        # --- Transmitters ---
        txs = meta.create_group('transmitters')
        for tx in transmitters:
            grp = txs.create_group(f'transmitter_{tx["id"]:03d}')
            grp.create_dataset('frequency_config', data=np.array([tx['freq'], tx['bw']], dtype=np.float64))
            grp.create_dataset('pri_config', data=np.array([tx['pri'], tx['pri_jitter']], dtype=np.float64))
            grp.create_dataset('pulse_width_config', data=np.array([tx['pw'], tx['pw_jitter']], dtype=np.float64))
            grp.create_dataset('position_config', data=np.array(tx['pos'], dtype=np.float64))
            grp.create_dataset('power_config', data=np.array([tx['peak_pwr'], tx['avg_pwr']], dtype=np.float64))

            scan_ds = grp.create_dataset('scan_config', data=np.array([tx['scan_rate'], tx['sector']], dtype=np.float64))
            scan_ds.attrs['scan_type'] = tx['type']

            grp.attrs['emitter_type'] = tx['type']
            grp.attrs['emitter_id'] = tx['id']

            if 'hop_freqs' in tx:
                grp.create_dataset('hop_frequencies', data=np.array(tx['hop_freqs'], dtype=np.float64))
            if 'on_sec' in tx:
                grp.create_dataset('duty_cycle', data=np.array([tx['on_sec'], tx['off_sec']], dtype=np.float64))

        # --- Generate Pulse Observations ---
        print("Generating pulse observations (this may take a moment)...")
        all_pulses = []

        for tx in transmitters:
            pri_sec = tx['pri'] / 1e6
            pw_sec = tx['pw'] / 1e6
            t = rng.uniform(0, pri_sec)  # random phase offset

            if tx['type'] == 'periodic':
                while t < sim_duration_sec:
                    jittered_pri = pri_sec * (1 + rng.normal(0, tx['pri_jitter']))
                    jittered_pw = tx['pw'] * (1 + rng.normal(0, tx['pw_jitter']))
                    freq = tx['freq'] + rng.normal(0, 0.5)
                    aoa = rng.uniform(0, 360)
                    amp = tx['peak_pwr'] + rng.normal(0, 2)
                    snr = amp - rng.uniform(5, 15)
                    all_pulses.append([t, freq, jittered_pw, aoa, amp, tx['id'], snr])
                    t += jittered_pri

            elif tx['type'] == 'frequency_agile':
                hop_freqs = tx.get('hop_freqs', [tx['freq']])
                hop_idx = 0
                hop_dwell = rng.uniform(0.5, 2.0)  # seconds per frequency
                last_hop_time = 0
                while t < sim_duration_sec:
                    if t - last_hop_time > hop_dwell:
                        hop_idx = (hop_idx + 1) % len(hop_freqs)
                        last_hop_time = t
                        hop_dwell = rng.uniform(0.5, 2.0)
                    jittered_pri = pri_sec * (1 + rng.normal(0, tx['pri_jitter']))
                    jittered_pw = tx['pw'] * (1 + rng.normal(0, tx['pw_jitter']))
                    freq = hop_freqs[hop_idx] + rng.normal(0, 1)
                    aoa = rng.uniform(0, 360)
                    amp = tx['peak_pwr'] + rng.normal(0, 2)
                    snr = amp - rng.uniform(5, 15)
                    all_pulses.append([t, freq, jittered_pw, aoa, amp, tx['id'], snr])
                    t += jittered_pri

            elif tx['type'] == 'intermittent':
                on_sec = tx.get('on_sec', 2.0)
                off_sec = tx.get('off_sec', 5.0)
                cycle = on_sec + off_sec
                while t < sim_duration_sec:
                    phase = t % cycle
                    if phase < on_sec:
                        jittered_pri = pri_sec * (1 + rng.normal(0, tx['pri_jitter']))
                        jittered_pw = tx['pw'] * (1 + rng.normal(0, tx['pw_jitter']))
                        freq = tx['freq'] + rng.normal(0, 0.5)
                        aoa = rng.uniform(0, 360)
                        amp = tx['peak_pwr'] + rng.normal(0, 2)
                        snr = amp - rng.uniform(5, 15)
                        all_pulses.append([t, freq, jittered_pw, aoa, amp, tx['id'], snr])
                        t += jittered_pri
                    else:
                        t += 0.01  # skip through off period quickly

        # Sort by time
        all_pulses.sort(key=lambda x: x[0])
        pulse_array = np.array(all_pulses, dtype=np.float64)

        # --- Observations ---
        obs = f.create_group('observations')
        pulse_ds = obs.create_dataset('pulses', data=pulse_array, compression='gzip')
        pulse_ds.attrs['columns'] = 'time_s,freq_mhz,pw_us,aoa_deg,amplitude_db,emitter_id,snr_db'
        pulse_ds.attrs['num_pulses'] = len(all_pulses)

        # Detection log (ground truth detections)
        det_times = np.linspace(0, sim_duration_sec, 500)
        detection_log = []
        for t_det in det_times:
            for tx in transmitters:
                is_det = False
                if tx['type'] == 'periodic':
                    is_det = True
                elif tx['type'] == 'frequency_agile':
                    is_det = True
                elif tx['type'] == 'intermittent':
                    cycle = tx.get('on_sec', 2) + tx.get('off_sec', 5)
                    is_det = (t_det % cycle) < tx.get('on_sec', 2)
                detection_log.append([t_det, tx['id'], tx['freq'], 1.0 if is_det else 0.0])

        det_array = np.array(detection_log, dtype=np.float64)
        det_ds = obs.create_dataset('detection_log', data=det_array, compression='gzip')
        det_ds.attrs['columns'] = 'time_s,emitter_id,freq_mhz,detected'

        # --- Scenario configs ---
        scen = f.create_group('scenarios')
        scen.attrs['periodic_ids'] = [1, 2, 3, 4, 5, 13]
        scen.attrs['frequency_agile_ids'] = [6, 7, 8, 9, 14]
        scen.attrs['intermittent_ids'] = [10, 11, 12, 15]
        scen.attrs['mixed_ids'] = list(range(1, 16))

    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Dataset generated at {output_path}")
    print(f"  Transmitters: {len(transmitters)}")
    print(f"  Total pulses: {len(all_pulses)}")
    print(f"  Duration: {sim_duration_sec}s")
    print(f"  File size: {file_size:.2f} MB")

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else None
    generate(path)
