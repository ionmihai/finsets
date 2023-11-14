# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/02_papers/hassan_etal_2019.ipynb.

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 4
from __future__ import annotations
import pandas as pd

import pandasmore as pdm
from .. import wrds
from ..fetch_tools import get_text_file_from_url

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'HOST_WEBSITE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET', 'ENTITY_ID_IN_CLEAN_DSET',
           'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'list_all_vars', 'get_raw_data', 'process_raw_data']

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 5
PROVIDER = 'Tarek A. Hassan, Stephan Hollander, Laurence van Lent, Ahmed Tahoun, 2019'
URL = 'https://www.dropbox.com/s/96xo9f1twlu3525/firmquarter_2022q1.csv?raw=1'
HOST_WEBSITE = 'https://www.firmlevelrisk.com/'
FREQ = 'Q'
MIN_YEAR = 2002
MAX_YEAR = 2022
ENTITY_ID_IN_RAW_DSET = 'gvkey'
ENTITY_ID_IN_CLEAN_DSET = 'permno'
TIME_VAR_IN_RAW_DSET = 'date'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 6
def list_all_vars(url: str=URL,
                  delimiter: str='\t'):
    df = get_text_file_from_url(url, nrows=1, delimiter=delimiter)

    return pd.DataFrame(list(df.columns), columns=['name'])

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 9
def get_raw_data(url: str=URL, 
            nrows: int=None, # How many rows to download. If None, all rows are downloaded
            delimiter: str='\t'
            ) -> pd.DataFrame:
    """Download raw data from `url`"""

    return get_text_file_from_url(url, nrows=nrows, delimiter=delimiter)

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 12
def process_raw_data(
        df: pd.DataFrame=None, # If None, will download using `download_raw`
        gvkey_permno_link: bool|pd.DataFrame=True, # Whether to download permno or not. If DataFrame, must contain `permno`, `gvkey`, and `Qdate`
        how: str='left' # How to merge permno into `df` if `gvkey_permno_link` is not False
) -> pd.DataFrame:
    """Converts `gvkey` to string and applies `pandasmore.setup_panel`. Adds `permno` if `gvkey_permno_link` is not False."""

    df = df.copy()

    df['gvkey'] = df['gvkey'].astype('string').str.zfill(6) #prepend 0's up to len 6
    df['date'] = df['date'].astype('string')

    # Format date variable so it can be converted into datetime (as the last day of the quarter)
    year = df['date'].str.slice(0, 4).astype('string')
    quarter = df['date'].str.slice(5, 6).astype('int')

    last_month = (quarter * 3).astype('string').str.zfill(2)
    last_day = last_month.map({'03': '31', '06': '30', '09': '30', '12': '31'})

    df['date'] = year + '-' + last_month + '-' + last_day

    df = pdm.setup_panel(df, panel_ids='gvkey', 
                        time_var='date', freq='Q',
                        panel_ids_toint=False,
                        drop_index_duplicates=True, duplicates_which_keep='last')
    
    if not gvkey_permno_link: return df
    else:    
      if gvkey_permno_link is True: gvkey_permno_link = wrds.linking.gvkey_permno_q()
      df = df.reset_index().merge(gvkey_permno_link, how=how, on=['gvkey','Qdate'])
      return pdm.setup_panel(df, panel_ids='permno', dates_processed=True, freq='Q',
                              drop_index_duplicates=True, duplicates_which_keep='last')
