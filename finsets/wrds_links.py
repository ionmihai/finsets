# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/wrds_links.ipynb.

# %% ../nbs/wrds_links.ipynb 2
from __future__ import annotations
from typing import List, Dict, Tuple, Callable
import os

import pandas as pd
import numpy as np
import wrds 

from . import wrds_utils

# %% auto 0
__all__ = ['gvkey_permno', 'merge_permno_into_gvkey']

# %% ../nbs/wrds_links.ipynb 3
def gvkey_permno(wrds_username: str=None,
                 ) -> pd.DataFrame:
    
    sql_string=f"""select gvkey, lpermno as permno, linktype, linkprim, linkdt, linkenddt
                    from crsp.ccmxpf_linktable
                    where substr(linktype,1,1)='L' and (linkprim ='C' or linkprim='P')"""
    
    df = wrds_utils.download(sql_string, wrds_username)
    df['linkdt'] = pd.to_datetime(df['linkdt'])
    df['linkenddt'] = pd.to_datetime(df['linkenddt'])
    df['linkenddt'] = df['linkenddt'].fillna(pd.to_datetime('today'))
    return df

# %% ../nbs/wrds_links.ipynb 5
def merge_permno_into_gvkey(dset_using_gvkey: pd.DataFrame, # DataFrame using `gvkey` 
          date_var: str='datadate', # Name of date variable in `dset_using_gvkey`
          date_var_format: str="%Y-%m-%d", # Format of `date_var` to be passed to `pd.to_datetime`
          gvkey_permno_link: pd.DataFrame=None, # Concordance DataFrame; will get downloaded if None
          ) -> pd.DataFrame:
    """Merges `permno` into `dset_using_gvkey` using `gvkey_permno_link`."""
    
    if gvkey_permno_link is None: gvkey_permno_link = gvkey_permno()
    df = dset_using_gvkey.merge(gvkey_permno_link, how='left', on=['gvkey'])
    df = df.dropna(subset=[date_var])

    df['dtdate'] = pd.to_datetime(df[date_var], format=date_var_format)    
    df = df[(df['dtdate']>=df['linkdt']) & (df['dtdate']<=df['linkenddt'])].copy()
    df = df.drop(columns = ['linktype', 'linkprim', 'linkdt', 'linkenddt'])
    return df
