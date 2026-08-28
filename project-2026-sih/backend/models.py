from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class Emitter:
    id: int
    frequency_mhz: float
    pri_us: float
    pulse_width_us: float
    position: List[float]
    power_dbm: float
    emitter_type: str  # 'periodic', 'frequency_agile', 'intermittent'
    scan_config: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

@dataclass 
class Pulse:
    time: float
    frequency_mhz: float
    pulse_width_us: float
    aoa_deg: float
    amplitude: float
    emitter_id: int

@dataclass
class FrequencyBand:
    id: int
    lower_mhz: float
    upper_mhz: float
    center_mhz: float

@dataclass
class ScanResult:
    band_id: int
    start_time: float
    duration: float
    result: str  # 'HIT' or 'MISS'
    detected_emitters: List[int] = field(default_factory=list)
    detected_pulses: List[dict] = field(default_factory=list)
    num_pulses: int = 0
