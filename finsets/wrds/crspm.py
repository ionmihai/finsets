# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/01_crspm.ipynb.

# %% ../../nbs/01_wrds/01_crspm.ipynb 3
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
__all__ = ['raw_metadata', 'raw_metadata_extra', 'default_raw_vars', 'parse_varlist', 'delist_adj_ret', 'download', 'clean']

# %% ../../nbs/01_wrds/01_crspm.ipynb 4
def raw_metadata(rawfile: str|Path=RESOURCES/'crspm_variable_descriptions.csv', # location of the raw variable labels file
             ) -> pd.DataFrame:
    "Loads raw variable labels file, cleans it and returns it as a pd.DataFrame"

    df = pd.read_csv(rawfile)
    df['output_of'] = 'wrds.crspm.clean'

    df['Variable Label'] = df.apply(lambda row: row['Description'].replace(row['Variable Name'].strip()+' -- ', ''), axis=1)
    df['Variable Label'] = df.apply(lambda row: row['Variable Label'].replace( '(' + row['Variable Name'].strip() + ')', ''), axis=1)
    df['Variable Name'] = df['Variable Name'].str.strip().str.lower()
    df = df[['Variable Name', 'Variable Label','output_of', 'Type']].copy()
    df.columns = ['name','label','output_of','type']
    return df

# %% ../../nbs/01_wrds/01_crspm.ipynb 7
def raw_metadata_extra(wrds_username: str=None
             ) -> pd.DataFrame:
    "Collects metadata from WRDS `crsp.msf` and `crsp.msenames` tables and merges it with `variable_labels`."

    if wrds_username is None:
        wrds_username = os.getenv('WRDS_USERNAME')
        if wrds_username is None: wrds_username = input("Enter your WRDS username: ") 

    try:
        db = wrds_api.Connection(wrds_username = wrds_username)
        msf = db.describe_table('crsp','msf')
        msf_rows = db.get_row_count('crsp','msf')
        mse = db.describe_table('crsp','msenames')
        mse_rows = db.get_row_count('crsp','msenames')
    finally:
        db.close()
        
    msf_meta = msf[['name','type']].copy()
    msf_meta['nr_rows'] = msf_rows
    msf_meta['wrds_library'] = 'crsp'
    msf_meta['wrds_table'] = 'msf'

    mse_meta = mse[['name','type']].copy()
    mse_meta['nr_rows'] = mse_rows
    mse_meta['wrds_library'] = 'crsp'
    mse_meta['wrds_table'] = 'msenames'

    crsp_meta = (pd.concat([msf_meta, mse_meta],axis=0, ignore_index=True)
                .merge(raw_metadata()[['name','label']], how='left', on='name'))
    
    crsp_meta['output_of'] = 'wrds.crspm.download()'
    crsp_meta = pdm.order_columns(crsp_meta,these_first=['name','label','output_of'])
    for v in list(crsp_meta.columns):
        crsp_meta[v] = crsp_meta[v].astype('string')
    
    return crsp_meta

# %% ../../nbs/01_wrds/01_crspm.ipynb 9
def default_raw_vars():
    """Default variables used in `download` if none are specified. Takes about 2 min to download."""
    
    return ['permno','permco','date',
            'ret', 'retx', 'shrout', 'prc', 
            'shrcd', 'exchcd','siccd','ticker','cusip','ncusip']            

# %% ../../nbs/01_wrds/01_crspm.ipynb 11
def parse_varlist(vars: List[str]=None,
                  wrds_username: str=None
                  ) -> str:
    """Figure out which `vars` come from the `crsp.msf` table and which come from the `crsp.msenames` table and add a. and b. prefixes"""

    if wrds_username is None:
        wrds_username = os.getenv('WRDS_USERNAME')
        if wrds_username is None: wrds_username = input("Enter your WRDS username: ") 

    if vars is None: vars = default_raw_vars()
    vars = ['permno','permco','date','exchcd'] + [x for x in vars if x not in ['permno','permco','date','exchcd']]

    try:
        db = wrds_api.Connection(wrds_username = wrds_username)
        all_msf_vars = list(db.describe_table('crsp','msf').name)
        all_mse_vars = list(db.describe_table('crsp','msenames').name)
        my_msf_vars = [f'a.{x}' for x in vars if x in all_msf_vars]
        my_mse_vars = [f'b.{x}' for x in vars if (x in all_mse_vars) and (x not in all_msf_vars)]
        varlist_string = ','.join(my_msf_vars + my_mse_vars)
    finally:
        db.close()
        
    return varlist_string

# %% ../../nbs/01_wrds/01_crspm.ipynb 12
def delist_adj_ret(df: pd.DataFrame, # Requires `ret`,`exchcd`, ` `dlret`, and `dlstcd` variables
                       adj_ret_var: str
                       ) -> pd.DataFrame:
    """Adjust for delisting returns using Shumway and Warther (1999) and Johnson and Zhao (2007)"""

    df['npdelist'] = (df['dlstcd']==500) | df['dlstcd'].between(520,584)
    df['dlret'] = np.where(df.dlret.isna() & df.npdelist & df.exchcd.isin([1,2]), -0.35, df.dlret)
    df['dlret'] = np.where(df.dlret.isna() & df.npdelist & df.exchcd.isin([3]), -0.55, df.dlret)
    df['dlret'] = np.where(df.dlret.notna() & df.dlret < -1, -1, df.dlret)
    df['dlret'] = df.dlret.fillna(0)

    df[adj_ret_var] = (1 + df.ret) * (1 + df.dlret) - 1
    df[adj_ret_var] = np.where(df[adj_ret_var].isna() & (df.dlret!=0), df.dlret, df[adj_ret_var])
    df = df.drop('npdelist', axis=1) 
    return df

# %% ../../nbs/01_wrds/01_crspm.ipynb 13
def download(vars: List[str]=None, # If None, downloads `default_raw_vars`; `permno`, `permco`, `date`, and 'exchcd' are added by default
             obs_limit: int=None,  #Number of rows to download. If None, full dataset will be downloaded             
             wrds_username: str=None,       #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
             start_date: str="01/01/1900",  # Start date in MM/DD/YYYY format
             end_date: str=None,            # End date in MM/DD/YYYY format; if None, defaults to current date  
             add_delist_adj_ret: bool=True, # Whether to calculate delisting-adjusted returns 
             adj_ret_var: str='ret_adj'     # What to call the returns adjusted for delisting bias
             ) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS crsp.msf and crsp.msenames libraries. 
        Creates `ret_adj` for delisting based on Shumway and Warther (1999) and Johnson and Zhao (2007)"""

    varlist_string = parse_varlist(vars, wrds_username)
    limit_clause = f"LIMIT {obs_limit}" if obs_limit is not None else ""
    sql_string = f"""SELECT {varlist_string},  c.dlstcd, c.dlret 
                        FROM crsp.msf AS a 
                        LEFT JOIN crsp.msenames AS b
                            ON a.permno=b.permno AND b.namedt<=a.date AND a.date<=b.nameendt                     
                        LEFT JOIN crsp.msedelist as c
                            ON a.permno=c.permno AND date_trunc('month', a.date) = date_trunc('month', c.dlstdt)                            
                            WHERE a.date BETWEEN '{start_date}' AND COALESCE(%(end)s, CURRENT_DATE) 
                    {limit_clause}
                """
    df = wrds_api.download(sql_string, wrds_username=wrds_username, params={'end':end_date})
    if add_delist_adj_ret: df = delist_adj_ret(df, adj_ret_var)
    else: df = df.drop(['dlret','dlstcd'], axis=1)
    return df 

# %% ../../nbs/01_wrds/01_crspm.ipynb 16
def clean(df: pd.DataFrame=None,        # If None, downloads `vars` using `download` function; else, must contain `permno` and `date` columns
          vars: List[str]=None,         # If None, downloads `default_raw_vars`
          obs_limit: int=None, #Number of rows to download. If None, full dataset will be downloaded
          wrds_username: str=None,      # If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
          start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
          end_date: str=None,           # End date. Default is current date          
          clean_kwargs: dict={},        # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
          ) -> pd.DataFrame:
    """Applies `pandasmore.setup_panel` to `df`. If `df` is None, downloads `vars` using `download` function."""

    if df is None: df = download(vars=vars, obs_limit=obs_limit, wrds_username=wrds_username, start_date=start_date, end_date=end_date)
    df = pdm.setup_panel(df, panel_ids='permno', time_var='date', freq='M', **clean_kwargs)
    return df 
