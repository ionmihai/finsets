# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/02_papers/peters_taylor_2016.ipynb.

# %% ../../nbs/02_papers/peters_taylor_2016.ipynb 2
from __future__ import annotations
from typing import List

import pandas as pd
import numpy as np

import pandasmore as pdm
from ..wrds import wrds_api

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'LIBRARY', 'TABLE', 'LINK_LIBRARY', 'LINK_TABLE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR',
           'ENTITY_ID_IN_RAW_DSET', 'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET',
           'list_all_vars', 'get_raw_data', 'process_raw_data', 'features']

# %% ../../nbs/02_papers/peters_taylor_2016.ipynb 3
PROVIDER = 'Wharton Research Data Services (WRDS)'
URL = 'https://wrds-www.wharton.upenn.edu/pages/get-data/peters-and-taylor-total-q/peters-and-taylor-total-q/'
LIBRARY = 'totalq'
TABLE = 'total_q'
LINK_LIBRARY = 'crsp'
LINK_TABLE = 'ccmxpf_lnkhist'
FREQ = 'A'
MIN_YEAR = 1950
MAX_YEAR = None
ENTITY_ID_IN_RAW_DSET = 'permno'
ENTITY_ID_IN_CLEAN_DSET = 'permno'
TIME_VAR_IN_RAW_DSET = 'datadate'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/02_papers/peters_taylor_2016.ipynb 4
def list_all_vars() -> pd.DataFrame:
    "Collects names of all available variables from WRDS f`{LIBRARY}.{TABLE}` and `{LIBRARY}.{COMPANY_TABLE}`."

    try:
        db = wrds_api.Connection()
        funda = db.describe_table(LIBRARY,TABLE).assign(wrds_library=LIBRARY, wrds_table=TABLE)
    finally:
        db.close()

    return funda[['name','type','wrds_library','wrds_table']].copy()

# %% ../../nbs/02_papers/peters_taylor_2016.ipynb 7
def get_raw_data(
        vars: List[str]='*', # Default is to get all available variables
        required_vars: List[str]=['gvkey','datadate'], #list of variables that will get downloaded, even if not in `vars`
        nrows: int=None, #Number of rows to download. If None, full dataset will be downloaded
        start_date: str=None, # Start date in MM/DD/YYYY format
        end_date: str=None #End date in MM/DD/YYYY format
) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS `{LIBRARY}.{TABLE}` library and adds PERMNO and PERMCO as in CCM"""
 
    wrds_api.validate_dates([start_date, end_date])

    sql_string=f"""SELECT c.lpermno as permno, c.lpermco as permco, c.liid, c.linkprim as linkprim, 
                          a.*, 
                          b.xrd, b.xsga, b.cogs, b.rdip, b.at, b.capx, b.ppegt, b.ppent, b.dp
                    FROM {LIBRARY}.{TABLE} AS a
                    LEFT JOIN comp.funda AS b ON a.gvkey = b.gvkey AND a.datadate = b.datadate
                    INNER JOIN {LINK_LIBRARY}.{LINK_TABLE} AS c ON a.gvkey = c.gvkey 
                    WHERE a.datadate BETWEEN c.linkdt AND COALESCE(c.linkenddt, CURRENT_DATE)
                            AND c.linktype IN ('LU','LC') AND c.linkprim IN ('P','C')
                """
    if start_date is not None: sql_string += r" AND a.datadate >= %(start_date)s"
    if end_date is not None: sql_string += r" AND a.datadate <= %(end_date)s"
    if nrows is not None: sql_string += r" LIMIT %(nrows)s"
    
    return wrds_api.download(sql_string,
                             params={'start_date':start_date, 'end_date':end_date, 'nrows':nrows})

# %% ../../nbs/02_papers/peters_taylor_2016.ipynb 9
def process_raw_data(
        df: pd.DataFrame=None,  # Must contain `permno` and `datadate` columns   
        clean_kwargs: dict={},  # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
) -> pd.DataFrame:
    """Applies `pandasmore.setup_panel` to `df`"""

    # Change some variables to categorical
    for col in ['permno','permco']:
        if col in df.columns:
            df[col] = df[col].astype('Int64').astype('category')

    for col in ['gvkey']:
        if col in df.columns:
            df[col] = df[col].astype('string').astype('category')
            
    # Set up panel structure
    df = pdm.setup_panel(df, panel_ids=ENTITY_ID_IN_RAW_DSET, time_var=TIME_VAR_IN_RAW_DSET, freq=FREQ, panel_ids_toint=False, **clean_kwargs)
    return df 

# %% ../../nbs/02_papers/peters_taylor_2016.ipynb 12
def features(df: pd.DataFrame=None
             ) -> pd.DataFrame:

    out = df.copy()

    for x in ['xrd','xsga']:
        out[f'{x}0'] = np.where(out[x].isnull() & out['at'].notnull(), 0, out[x])
        out[f'{x}0'] = np.where(out[f'{x}0'].isnull() & out['at'].isnull(), out[f'{x}0'].interpolate(), out[f'{x}0'])

    out['sga'] = np.where(out['xsga'].isnull() | out['xrd0'].between(out['xsga0'],out['cogs']) 
                        ,out['xsga0'].fillna(0),
                        out['xsga0'] - out['xrd0'] - out['rdip'].fillna(0))    

    out['k_phy'] = out['ppegt']
    out['k_tot'] = out['k_phy'] + out['k_int']

    out['i_phy'] = out['capx']
    out['i_int'] = out['xrd0'] + 0.3*out['sga']
    out['i_tot'] = out['i_phy'] + out['i_int']

    out['i2k_int'] = out['i_int'] / pdm.lag(out['k_tot'])
    out['i2k_phy'] = out['i_phy'] / pdm.lag(out['k_tot'])
    out['i2k_tot'] = out['i2k_int'] + out['i2k_phy']    

    out = out.replace([np.inf, -np.inf], np.nan)
    return out 

