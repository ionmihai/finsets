# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/05_ratios.ipynb.

# %% ../../nbs/01_wrds/05_ratios.ipynb 3
from __future__ import annotations
from typing import List

import pandas as pd

import pandasmore as pdm
from . import wrds_api

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'LIBRARY', 'TABLE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET',
           'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'list_all_vars', 'get_raw_data',
           'process_raw_data', 'keep_only_ratios']

# %% ../../nbs/01_wrds/05_ratios.ipynb 4
PROVIDER = 'Wharton Research Data Services (WRDS)'
URL = 'https://wrds-www.wharton.upenn.edu/pages/get-data/financial-ratios-suite-wrds/financial-ratios-with-ibes-subscription/financial-ratios-firm-level-ibes/'
LIBRARY = 'wrdsapps_finratio_ibes'
TABLE = 'firm_ratio_ibes'
FREQ = 'M'
MIN_YEAR = 1970
MAX_YEAR = None
ENTITY_ID_IN_RAW_DSET = 'permno'
ENTITY_ID_IN_CLEAN_DSET = 'permno'
TIME_VAR_IN_RAW_DSET = 'public_date'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/01_wrds/05_ratios.ipynb 5
def list_all_vars() -> pd.DataFrame:
    "Collects names of all available variables from WRDS f`{LIBRARY}.{TABLE}`"

    try:
        db = wrds_api.Connection()
        funda = db.describe_table(LIBRARY,TABLE).assign(wrds_library=LIBRARY, wrds_table=TABLE)
    finally:
        db.close()

    return funda[['name','type','wrds_library','wrds_table']]

# %% ../../nbs/01_wrds/05_ratios.ipynb 8
def get_raw_data(vars: List[str]=None, # If None or '*', downloads all variables
             nrows: int=None, #Number of rows to download. If None, full dataset will be downloaded
             start_date: str=None, # Start date in MM/DD/YYYY format
             end_date: str=None #End date in MM/DD/YYYY format
             ) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS `{LIBRARY}.{TABLE}` library"""

    wrds_api.validate_dates([start_date, end_date])
    if vars is None or vars=='*': vars = '*'
    else: vars = ','.join(['public_date','permno'] + [f'{x}' for x in vars if x not in ['public_date', 'permno']])

    sql_string=f"""SELECT {vars} FROM {LIBRARY}.{TABLE} WHERE 1 = 1 """
    if start_date is not None: sql_string += r" AND public_date >= %(start_date)s"
    if end_date is not None: sql_string += r" AND public_date <= %(end_date)s"
    if nrows is not None: sql_string += r" LIMIT %(nrows)s"

    return wrds_api.download(sql_string,
                            params={'start_date':start_date, 'end_date':end_date, 'nrows':nrows})

# %% ../../nbs/01_wrds/05_ratios.ipynb 11
def process_raw_data(
        df: pd.DataFrame=None,  # Must contain `permno` and `datadate` columns         
        clean_kwargs: dict={},  # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
) -> pd.DataFrame:
    """Converts some variables to categorical and applies `pandasmore.setup_panel` to `df`"""

    # Convert some columns to categorical
    for col in ['gvkey','ticker','cusip','gsector','gicdesc']:
        if col in df.columns: df[col] = df[col].astype('category')

    for col in df.columns:
        if col.startswith('ffi'):
            if col.endswith('desc'): df[col] = df[col].astype('category')
            else: df[col] = df[col].astype('Int64').astype('category')

    # Set panel structure     
    df = pdm.setup_panel(df, panel_ids=ENTITY_ID_IN_RAW_DSET, time_var=TIME_VAR_IN_RAW_DSET, freq=FREQ, panel_ids_toint=False, **clean_kwargs)
    return df 

# %% ../../nbs/01_wrds/05_ratios.ipynb 14
def keep_only_ratios(
        df: pd.DataFrame
) -> pd.DataFrame:
    
    out = pd.DataFrame(index=df.index)

    not_ratios = r"""be, mktcap, price, dtdate, permno, gvkey, ticker, 
                    cusip, public_date, adate, qdate, gsector, gicdesc,
                """.replace("\n", "").replace(' ','').split(',')
    
    for col in list(df.columns):
        if col not in not_ratios and not col.startswith('ffi'):
            out[col] = df[col].copy()

    return out
