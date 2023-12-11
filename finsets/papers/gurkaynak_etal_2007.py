# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/02_papers/gurkaynak_etal_2007.ipynb.

# %% ../../nbs/02_papers/gurkaynak_etal_2007.ipynb 4
from __future__ import annotations
import os

import pandas as pd

import pandasmore as pdm
from ..fetch_tools import get_text_file_from_url

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'HOST_WEBSITE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET',
           'get_raw_data', 'list_all_vars', 'process_raw_data']

# %% ../../nbs/02_papers/gurkaynak_etal_2007.ipynb 5
PROVIDER = 'Gürkaynak, Refet S, Brian Sack, and Jonathan H Wright, 2007'
URL = 'https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv'
HOST_WEBSITE = 'https://www.federalreserve.gov/data/nominal-yield-curve.htm'
FREQ = 'D'
MIN_YEAR = 1961
MAX_YEAR = None
TIME_VAR_IN_RAW_DSET = 'Date'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/02_papers/gurkaynak_etal_2007.ipynb 9
def get_raw_data(url: str=URL, 
            nrows: int=None, # How many rows to download. If None, all rows are downloaded
            delimiter: str=',',
            skiprows: int=9,
            headers: dict=None,
            ) -> pd.DataFrame:
    """Download raw data from `url`"""
    if headers is None: headers = {'User-Agent': os.getenv('USER_AGENT', None)}
    if headers is None: print('No headers are provided. This may cause problems.')

    return get_text_file_from_url(url, nrows=nrows, delimiter=delimiter, skiprows=skiprows, headers=headers)

# %% ../../nbs/02_papers/gurkaynak_etal_2007.ipynb 12
def list_all_vars():
    return pd.DataFrame(list(get_raw_data(nrows=1).columns), columns=['name'])

# %% ../../nbs/02_papers/gurkaynak_etal_2007.ipynb 14
def process_raw_data(df: pd.DataFrame=None
                     ) -> pd.DataFrame:
    
    return pdm.setup_tseries(df, time_var=TIME_VAR_IN_RAW_DSET, freq=FREQ)
