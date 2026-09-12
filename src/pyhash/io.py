from __future__ import annotations
from pathlib import Path
import pandas as pd
from .legacy import in_pol,in_sp,in_sta,in_other

def read_polarities(path, input_format='skhash', merge_on=()):
    return in_pol.read_polarity_file(str(path),input_format,list(merge_on))

def read_catalog(path):
    p={'catfile':str(path),'input_format':'skhash'}
    return in_other.read_catalog_file(p)

def read_station_file(pol_df,p_dict):
    return in_sta.read_station_file(pol_df,p_dict)

def read_amplitudes(path,input_format='skhash',merge_on=(),ratmin=3.0,min_sp=5e-4,max_sp=2000):
    return in_sp.read_amp_file(str(path),input_format,list(merge_on),ratmin,min_sp,max_sp)

def read_csv(path, **kwargs):
    return pd.read_csv(Path(path),**kwargs)
