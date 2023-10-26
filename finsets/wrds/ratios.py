# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/05_ratios.ipynb.

# %% ../../nbs/01_wrds/05_ratios.ipynb 3
from __future__ import annotations
from pathlib import Path
from typing import List
import os

import pandas as pd
import numpy as np

import pandasmore as pdm
from . import wrds_api
from .. import RESOURCES

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'LIBRARY', 'TABLE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET',
           'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'LABELS_FILE', 'raw_metadata',
           'download', 'clean']

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
TIME_VAR_IN_CLEAN_DSET = 'Mdate'
LABELS_FILE = RESOURCES/'finratio_firm_ibes_variable_descriptions.csv'

# %% ../../nbs/01_wrds/05_ratios.ipynb 5
def raw_metadata(wrds_username: str=None
             ) -> pd.DataFrame:
    "Collects metadata from WRDS `{LIBRARY}.{TABLE}` and merges it with variable labels from LABELS_FILE."

    # Get metadata from `{LIBRARY}.{TABLE}`
    if wrds_username is None:
        wrds_username = os.getenv('WRDS_USERNAME')
        if wrds_username is None: wrds_username = input("Enter your WRDS username: ") 
    try:
        db = wrds_api.Connection(wrds_username = wrds_username)
        finr = db.describe_table(LIBRARY,TABLE)
        finr_rows = db.get_row_count(LIBRARY,TABLE)
    finally:
        db.close()
        
    finr_meta = finr[['name','type']].copy()
    finr_meta['nr_rows'] = finr_rows
    finr_meta['wrds_library'] = LIBRARY
    finr_meta['wrds_table'] = TABLE

    # Get variable labels from LABELS_FILE
    df = pd.read_csv(LABELS_FILE)
    df['Variable Label'] = df.apply(lambda row: row['Description'].replace(row['Variable Name'].strip()+' -- ', ''), axis=1)
    df['Variable Label'] = df.apply(lambda row: row['Variable Label'].replace( '(' + row['Variable Name'].strip() + ')', ''), axis=1)
    df['Variable Name'] = df['Variable Name'].str.strip().str.lower()
    df = df[['Variable Name', 'Variable Label', 'Group']].copy()
    df.columns = ['name','label','group']

    # Merge metadata with labels and clean up a bit
    df = finr_meta.merge(df, how='left', on='name')
    df['output_of'] = 'wrds.ratios.download'
    df = pdm.order_columns(df,these_first=['name','label','output_of'])
    for v in list(df.columns):
        df[v] = df[v].astype('string')
    
    return df

# %% ../../nbs/01_wrds/05_ratios.ipynb 8
def download(vars: List[str]=None, # If None, downloads all variables
             obs_limit: int=None, #Number of rows to download. If None, full dataset will be downloaded
             wrds_username: str=None, #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
             start_date: str=None, # Start date in MM/DD/YYYY format
             end_date: str=None #End date in MM/DD/YYYY format
             ) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS `{LIBRARY}.{TABLE}` library"""

    if vars is None: 
        vars = '*'
    else:
        vars = ','.join(['public_date','permno'] + [f'{x}' for x in vars if x not in ['public_date', 'permno']])

    sql_string=f"""SELECT {vars} FROM {LIBRARY}.{TABLE} WHERE 1 = 1 """
    if start_date is not None: sql_string += r" AND public_date >= %(start_date)s"
    if end_date is not None: sql_string += r" AND public_date <= %(end_date)s"
    if obs_limit is not None: sql_string += r" LIMIT %(obs_limit)s"

    return wrds_api.download(sql_string, wrds_username=wrds_username, 
                             params={'start_date':start_date, 'end_date':end_date, 'obs_limit':obs_limit})

# %% ../../nbs/01_wrds/05_ratios.ipynb 12
def clean(df: pd.DataFrame=None,        # If None, downloads `vars` using `download` function; else, must contain `permno` and `date` columns
          vars: List[str]=None,         # If None, downloads `default_raw_vars`
          obs_limit: int=None,          # Number of rows to download. If None, full dataset will be downloaded
          wrds_username: str=None,      # If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
          start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
          end_date: str=None,           # End date. Default is current date          
          clean_kwargs: dict={},        # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
          ) -> pd.DataFrame:
    """Applies `pandasmore.setup_panel` to `df`. If `df` is None, downloads `vars` using `download` function."""

    if df is None: df = download(vars=vars, obs_limit=obs_limit, wrds_username=wrds_username, start_date=start_date, end_date=end_date)
    df = pdm.setup_panel(df, panel_ids=ENTITY_ID_IN_CLEAN_DSET, time_var=TIME_VAR_IN_RAW_DSET, freq=FREQ, **clean_kwargs)
    return df 
