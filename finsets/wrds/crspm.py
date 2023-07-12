# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/01_crspm.ipynb.

# %% auto 0
__all__ = ['default_raw_vars', 'download', 'clean']

# %% ../../nbs/01_wrds/01_crspm.ipynb 3
from typing import List
import os

import pandas as pd
import numpy as np

import pandasmore as pdm
from . import wrds_api

# %% ../../nbs/01_wrds/01_crspm.ipynb 4
def default_raw_vars():
    """Default variables used in `download` if none are specified. Takes about 2 min to download."""
    
    return ['permno','permco','date',
            'ret', 'retx', 'shrout', 'prc', 
            'shrcd', 'exchcd','siccd','ticker','cusip','ncusip']            

# %% ../../nbs/01_wrds/01_crspm.ipynb 8
def download(vars: List[str]=None, # If None, downloads `default_raw_vars`; else `permno`, `permco`, `date`, and 'exchcd' are added by default
             wrds_username: str=None, #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
             start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
             end_date: str=None, # End date in MM/DD/YYYY format; if None, defaults to current date  
             add_delist_adj_ret: bool=True, # Whether to calculate delisting-adjusted returns 
             adj_ret_var: str='ret_adj' # What to call the returns adjusted for delisting bias
             ) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS crsp.msf and crsp.msenames libraries. 
        Creates `ret_adj` for delisting based on Shumway and Warther (1999) and Johnson and Zhao (2007)"""

    varlist_string = parse_varlist(vars, wrds_username)
    sql_string = f"""SELECT {varlist_string},  c.dlstcd, c.dlret 
                        FROM crsp.msf AS a 
                        LEFT JOIN crsp.msenames AS b
                            ON a.permno=b.permno AND b.namedt<=a.date AND a.date<=b.nameendt                     
                        LEFT JOIN crsp.msedelist as c
                            ON a.permno=c.permno AND date_trunc('month', a.date) = date_trunc('month', c.dlstdt)                            
                            WHERE a.date BETWEEN '{start_date}' AND COALESCE(%(end)s, CURRENT_DATE) 
                """
    df = wrds_api.download(sql_string, wrds_username=wrds_username, params={'end':end_date})
    if add_delist_adj_ret: df = delist_adj_ret(df, adj_ret_var)
    else: df = df.drop(['dlret','dlstcd'], axis=1)
    return df 

# %% ../../nbs/01_wrds/01_crspm.ipynb 11
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
