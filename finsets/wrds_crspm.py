# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/wrds_crspm.ipynb.

# %% ../nbs/wrds_crspm.ipynb 2
from __future__ import annotations
from typing import List, Dict, Tuple, Callable
import os

import pandas as pd
import numpy as np
import wrds

import pandasmore as pdm
from . import wrds_utils, wrds_links

# %% auto 0
__all__ = ['default_raw_vars', 'download', 'clean']

# %% ../nbs/wrds_crspm.ipynb 3
def default_raw_vars():
    """Default variables used in `download` if none are specified. Takes about 2 min to download."""
    return ['permno','permco','date',
            'ret', 'retx', 'shrout', 'prc', 
            'shrcd', 'exchcd','siccd','ticker','cusip','ncusip']            

# %% ../nbs/wrds_crspm.ipynb 5
def download(vars: List[str]=None, # If None, downloads `default_raw_vars`; else `permno`, `permco`, and `date` are added by default
             wrds_username: str=None, #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
             start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
             end_date: str=None # End date. Default is current date             
             ) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS crsp.msf and crsp.msenames libraries"""

    if wrds_username is None:
        wrds_username = os.getenv('WRDS_USERNAME')
        if wrds_username is None: wrds_username = input("Enter your WRDS username: ") 

    if vars is None: vars = default_raw_vars()
    vars = ['permno','permco','date'] + [x for x in vars if x not in ['permno','permco','date']]

    # Figure out which `vars` come from the `msf` table and which come from the `msenames` table and add a. and b. prefixes
    db = wrds.Connection(wrds_username = wrds_username)
    try:
        all_msf_vars = list(db.describe_table('crsp','msf').name)
        all_mse_vars = list(db.describe_table('crsp','msenames').name)
        my_msf_vars = [f'a.{x}' for x in vars if x in all_msf_vars]
        my_mse_vars = [f'b.{x}' for x in vars if (x in all_mse_vars) and (x not in all_msf_vars)]
        varlist_string = ','.join(my_msf_vars + my_mse_vars)
    except:
        raise RuntimeError("Something went wrong with a WRDS database connection")
    finally: db.close()

    sql_string = f"""SELECT {varlist_string} 
                        FROM crsp.msf AS a 
                        LEFT JOIN crsp.msenames AS b
                            ON a.permno=b.permno AND b.namedt<=a.date AND a.date<=b.nameendt
                            WHERE a.date BETWEEN '{start_date}' AND COALESCE(%(end)s, CURRENT_DATE) 
                """
    return wrds_utils.download(sql_string, wrds_username=wrds_username, params={'end':end_date})

# %% ../nbs/wrds_crspm.ipynb 8
def clean(df: pd.DataFrame=None, # If None, downloads `vars` using `download` function; else, must contain `permno` and `date` columns
          vars: List[str]=None, # If None, downloads `default_raw_vars`
          wrds_username: str=None, #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
          start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
          end_date: str=None, # End date. Default is current date          
          clean_kwargs: dict={}, # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
          ) -> pd.DataFrame:
    """Applies `pandasmore.setup_panel` to `df`. If `df` is None, downloads `vars` using `download` function."""

    if df is None: df = download(vars=vars, wrds_username=wrds_username, start_date=start_date, end_date=end_date)
    df = pdm.setup_panel(df, panel_ids='permno', time_var='date', freq='M', **clean_kwargs)
    return df 
