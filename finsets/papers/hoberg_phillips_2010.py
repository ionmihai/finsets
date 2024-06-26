# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/02_papers/hoberg_phillips_2020.ipynb.

# %% ../../nbs/02_papers/hoberg_phillips_2020.ipynb 4
from __future__ import annotations
from pathlib import Path 
import os

import requests
import zipfile
import io
import pandas as pd

from .. import wrds

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'TXT_FILE', 'HOST_WEBSITE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET',
           'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'get_raw_data',
           'process_raw_data']

# %% ../../nbs/02_papers/hoberg_phillips_2020.ipynb 5
PROVIDER = 'Gerard Hoberg and Gordon Phillips, 2010, 2016'
URL = 'https://hobergphillips.tuck.dartmouth.edu/idata/tnic3_data.zip' 
TXT_FILE = 'tnic3_data.txt'
HOST_WEBSITE = 'https://hobergphillips.tuck.dartmouth.edu/industryclass.htm'
FREQ = 'A'
MIN_YEAR = 1989
MAX_YEAR = 2021
ENTITY_ID_IN_RAW_DSET = 'gvkey' 
ENTITY_ID_IN_CLEAN_DSET = 'gvkey' 
TIME_VAR_IN_RAW_DSET = 'date'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/02_papers/hoberg_phillips_2020.ipynb 7
def get_raw_data(url: str=URL,
                 txt_file: str=TXT_FILE, # Name of the data txt file inside the zip file found at `url` 
            ) -> pd.DataFrame:
    """Download raw data from `url`"""

    response = requests.get(url)
    if response.status_code == 200:
        # Decompress the file first with zip
        with io.BytesIO(response.content) as compressed_file:
            with zipfile.ZipFile(compressed_file, 'r') as zip_ref:
                with zip_ref.open(txt_file) as data_file:
                    df = pd.read_csv(io.BytesIO(data_file.read()),delimiter='\t' ,header=0)
    else:
        print("Failed to download the file. Status code:", response.status_code)
    
    return df

# %% ../../nbs/02_papers/hoberg_phillips_2020.ipynb 10
def process_raw_data(df: pd.DataFrame=None,
                     gvkey_to_permno: bool|pd.DataFrame=True, # Whether to download permno-gvkey link. If DataFrame, must contain 'gvkey'
                     ) -> pd.DataFrame:
    """Cleans up dates and optionally adds CRSP permnos"""

    df['Adate'] = pd.to_datetime(df.year.astype('string'), format="%Y").dt.to_period('A')
    df = df.drop('year',axis=1).dropna().copy()

    if not gvkey_to_permno: return df
    if gvkey_to_permno is True: permnos = wrds.linking.gvkey_permno_a()
    permnos['gvkey'] = permnos.gvkey.astype('int64')

    df = (df.merge(permnos.rename(columns={'permno':'permno1', 'gvkey':'gvkey1'}), how='left', on=['Adate','gvkey1'])
            .merge(permnos.rename(columns={'permno':'permno2', 'gvkey':'gvkey2'}), how='left', on=['Adate','gvkey2']))
    return df 
