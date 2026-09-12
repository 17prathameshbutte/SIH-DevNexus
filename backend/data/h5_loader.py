"""Dynamic HDF5 dataset loader that adapts to discovered structure."""
import h5py
import numpy as np
import logging
from typing import List, Dict, Any
from models import Emitter, Pulse

logger = logging.getLogger(__name__)


class H5Loader:
    """Loads emitter metadata and pulse observations from HDF5 files."""

    def load(self, filepath: str) -> dict:
        result = {'emitters': [], 'pulses': [], 'metadata': {}}
        try:
            with h5py.File(filepath, 'r') as f:
                # Load metadata
                result['metadata'] = self._load_metadata(f)

                # Load emitters
                result['emitters'] = self._load_emitters(f)

                # Load pulses (vectorized for performance)
                result['pulses'] = self._load_pulses(f)

        except FileNotFoundError:
            logger.error(f"H5 file not found: {filepath}")
        except Exception as e:
            logger.error(f"Error loading H5 file: {e}")
            raise
        return result

    def _load_metadata(self, f: h5py.File) -> dict:
        metadata = {}
        if 'metadata' in f:
            if 'simulation_info' in f['metadata']:
                sim_info = f['metadata/simulation_info']
                metadata = {k: self._convert_value(v) for k, v in sim_info.attrs.items()}
        return metadata

    def _load_emitters(self, f: h5py.File) -> List[Emitter]:
        emitters = []

        # Try standard structure: metadata/transmitters/transmitter_XXX
        tx_paths = []
        if 'metadata/transmitters' in f:
            tx_group = f['metadata/transmitters']
            tx_paths = [(name, tx_group[name]) for name in sorted(tx_group.keys())]
        elif 'transmitters' in f:
            tx_group = f['transmitters']
            tx_paths = [(name, tx_group[name]) for name in sorted(tx_group.keys())]

        for tx_name, tx_grp in tx_paths:
            try:
                emitter = self._parse_emitter(tx_name, tx_grp, len(emitters) + 1)
                if emitter:
                    emitters.append(emitter)
            except Exception as e:
                logger.warning(f"Could not load transmitter {tx_name}: {e}")

        logger.info(f"Loaded {len(emitters)} emitters")
        return emitters

    def _parse_emitter(self, name: str, grp: h5py.Group, default_id: int) -> Emitter:
        """Parse a single emitter from an HDF5 group, adapting to available fields."""
        # Get ID from attribute or name
        emitter_id = default_id
        if 'emitter_id' in grp.attrs:
            emitter_id = int(grp.attrs['emitter_id'])
        else:
            # Try parsing from name like 'transmitter_003'
            try:
                emitter_id = int(name.split('_')[-1])
            except (ValueError, IndexError):
                pass

        # Frequency
        freq = self._get_dataset_value(grp, ['frequency_config', 'frequency', 'freq'], index=0, default=0.0)

        # PRI
        pri = self._get_dataset_value(grp, ['pri_config', 'pri', 'pulse_repetition_interval'], index=0, default=1000.0)

        # Pulse width
        pw = self._get_dataset_value(grp, ['pulse_width_config', 'pulse_width', 'pw'], index=0, default=5.0)

        # Position
        pos_data = self._get_dataset_array(grp, ['position_config', 'position', 'pos'])
        position = [float(x) for x in pos_data] if pos_data is not None else [0.0, 0.0, 0.0]

        # Power
        power = self._get_dataset_value(grp, ['power_config', 'power', 'peak_power'], index=0, default=50.0)

        # Emitter type
        emitter_type = 'periodic'
        if 'emitter_type' in grp.attrs:
            emitter_type = str(grp.attrs['emitter_type'])
        elif 'scan_config' in grp:
            sc = grp['scan_config']
            if 'scan_type' in sc.attrs:
                emitter_type = str(sc.attrs['scan_type'])

        # Scan config (all attributes from scan_config dataset)
        scan_config = {}
        if 'scan_config' in grp:
            sc = grp['scan_config']
            scan_config = {k: self._convert_value(v) for k, v in sc.attrs.items()}
            scan_data = sc[:]
            if len(scan_data) >= 2:
                scan_config['scan_rate'] = float(scan_data[0])
                scan_config['sector_width'] = float(scan_data[1])

        # Hop frequencies (for frequency-agile emitters)
        if 'hop_frequencies' in grp:
            scan_config['hop_frequencies'] = [float(x) for x in grp['hop_frequencies'][:]]

        # Duty cycle (for intermittent emitters)
        if 'duty_cycle' in grp:
            dc = grp['duty_cycle'][:]
            scan_config['on_sec'] = float(dc[0])
            scan_config['off_sec'] = float(dc[1])

        return Emitter(
            id=emitter_id,
            frequency_mhz=float(freq),
            pri_us=float(pri),
            pulse_width_us=float(pw),
            position=position,
            power_dbm=float(power),
            emitter_type=emitter_type,
            scan_config=scan_config,
            active=True
        )

    def _load_pulses(self, f: h5py.File) -> List[Pulse]:
        """Load pulse observations using vectorized numpy operations."""
        pulses = []

        # Try standard path
        pulse_ds = None
        for path in ['observations/pulses', 'pulses', 'observations/pdw']:
            if path in f:
                pulse_ds = f[path]
                break

        if pulse_ds is None:
            logger.info("No pulse data found in H5 file")
            return pulses

        # Load entire dataset as numpy array (fast)
        data = pulse_ds[:]
        if len(data) == 0:
            return pulses

        # Get column mapping from attributes
        col_str = ''
        if 'columns' in pulse_ds.attrs:
            col_str = str(pulse_ds.attrs['columns'])

        # Default column order: time, freq, pw, aoa, amplitude, emitter_id, snr
        ncols = data.shape[1] if len(data.shape) > 1 else 1

        # Vectorized conversion (much faster than row-by-row)
        logger.info(f"Loading {len(data)} pulses...")
        for i in range(min(len(data), 100000)):  # Cap at 100k for memory
            row = data[i]
            pulse = Pulse(
                time=float(row[0]) if ncols > 0 else 0.0,
                frequency_mhz=float(row[1]) if ncols > 1 else 0.0,
                pulse_width_us=float(row[2]) if ncols > 2 else 0.0,
                aoa_deg=float(row[3]) if ncols > 3 else 0.0,
                amplitude=float(row[4]) if ncols > 4 else 0.0,
                emitter_id=int(row[5]) if ncols > 5 else 0
            )
            pulses.append(pulse)

        logger.info(f"Loaded {len(pulses)} pulses")
        return pulses

    def _get_dataset_value(self, grp, keys, index=0, default=0.0):
        """Try multiple dataset names and return value at index."""
        for key in keys:
            if key in grp:
                ds = grp[key]
                data = ds[:]
                if len(data) > index:
                    return float(data[index])
        return default

    def _get_dataset_array(self, grp, keys):
        """Try multiple dataset names and return full array."""
        for key in keys:
            if key in grp:
                return grp[key][:]
        return None

    def _convert_value(self, val):
        """Convert HDF5 attribute values to JSON-serializable Python types."""
        if isinstance(val, bytes):
            return val.decode('utf-8')
        elif isinstance(val, np.integer):
            return int(val)
        elif isinstance(val, np.floating):
            return float(val)
        elif isinstance(val, np.ndarray):
            return val.tolist()
        return val
