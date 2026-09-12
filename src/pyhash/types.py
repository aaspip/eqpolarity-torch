from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True)
class ObservationSet:
    azimuth: np.ndarray
    takeoff: np.ndarray
    polarity: np.ndarray
    sp_ratio: np.ndarray | None = None
    station: np.ndarray | None = None

    def __post_init__(self):
        self.azimuth=np.asarray(self.azimuth,float)
        self.takeoff=np.asarray(self.takeoff,float)
        self.polarity=np.asarray(self.polarity,float)
        if self.azimuth.ndim==1: self.azimuth=self.azimuth[:,None]
        if self.takeoff.ndim==1: self.takeoff=self.takeoff[:,None]
        if self.azimuth.shape != self.takeoff.shape:
            raise ValueError('azimuth and takeoff must have identical (nobs,ntrial) shapes')
        if len(self.polarity)!=self.azimuth.shape[0]:
            raise ValueError('polarity length must equal number of observations')
        if self.sp_ratio is None:
            self.sp_ratio=np.full(len(self.polarity),np.nan)
        else:
            self.sp_ratio=np.asarray(self.sp_ratio,float)
            if len(self.sp_ratio)!=len(self.polarity): raise ValueError('sp_ratio length mismatch')

@dataclass(slots=True)
class GridSearchResult:
    fault_normals: np.ndarray
    fault_slips: np.ndarray
    indices: np.ndarray
    backend: str
    n_candidates: int
    n_accepted: int

@dataclass(slots=True)
class Mechanism:
    strike: float
    dip: float
    rake: float
    probability: float = 1.0
    rms_difference: float = float('nan')
    quality: str = ''
