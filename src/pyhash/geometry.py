from __future__ import annotations
import numpy as np
from .legacy import fun as _f

vector_from_sdr=_f.vector_from_sdr
sdr_from_vector=_f.sdr_from_vector
average_mechanism=_f.average_mech
mechanism_rotation=_f.mech_rotation
circular_std=_f.circstd

def maximum_gaps(azimuth_deg, takeoff_deg):
    return _f.determine_max_gap(np.asarray(azimuth_deg,float),np.asarray(takeoff_deg,float))

def radiation_misfit(azimuth,takeoff,polarity,sp_ratio,strike,dip,rake):
    return _f.calculate_misfit(np.asarray(azimuth,float),np.asarray(takeoff,float),np.asarray(polarity,float),np.asarray(sp_ratio,float),strike,dip,rake)
