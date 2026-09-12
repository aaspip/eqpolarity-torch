"""PyHASH: robust HASH/SKHASH-compatible focal-mechanism inversion for eqpolarity-torch."""
from .config import HashConfig
from .types import ObservationSet,GridSearchResult,Mechanism
from .grid import direction_grid,search,search_numpy,search_torch
from .solver import solve
from .geometry import vector_from_sdr,sdr_from_vector,maximum_gaps
__version__='0.1.0'
__all__=['HashConfig','ObservationSet','GridSearchResult','Mechanism','direction_grid','search','search_numpy','search_torch','solve','vector_from_sdr','sdr_from_vector','maximum_gaps']
