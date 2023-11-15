# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/04_compq.ipynb.

# %% ../../nbs/01_wrds/04_compq.ipynb 2
from __future__ import annotations
from typing import List

import pandas as pd
import numpy as np

import pandasmore as pdm
from . import wrds_api

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'LIBRARY', 'TABLE', 'COMPANY_TABLE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET',
           'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'list_all_vars',
           'default_raw_vars', 'parse_varlist', 'get_raw_data', 'process_raw_data', 'ytd_to_quarterly', 'features']

# %% ../../nbs/01_wrds/04_compq.ipynb 3
PROVIDER = 'Wharton Research Data Services (WRDS)'
URL = 'https://wrds-www.wharton.upenn.edu/pages/get-data/compustat-capital-iq-standard-poors/compustat/north-america-daily/fundamentals-quarterly/'
LIBRARY = 'comp'
TABLE = 'fundq'
COMPANY_TABLE = 'company' #contains some header information that is missing from comp.funda (e.g. sic and naics) 
FREQ = 'Q'
MIN_YEAR = 1961
MAX_YEAR = None
ENTITY_ID_IN_RAW_DSET = 'gvkey'
ENTITY_ID_IN_CLEAN_DSET = 'gvkey'
TIME_VAR_IN_RAW_DSET = 'datadate'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/01_wrds/04_compq.ipynb 4
def list_all_vars() -> pd.DataFrame:
    "Collects names of all available variables from WRDS f`{LIBRARY}.{TABLE}` and `{LIBRARY}.{COMPANY_TABLE}`."

    try:
        db = wrds_api.Connection()
        funda = db.describe_table(LIBRARY,TABLE).assign(wrds_library=LIBRARY, wrds_table=TABLE)
        fundn = db.describe_table(LIBRARY,COMPANY_TABLE).assign(wrds_library=LIBRARY, wrds_table=COMPANY_TABLE)
    finally:
        db.close()

    return pd.concat([funda,fundn])[['name','type','wrds_library','wrds_table']].copy()

# %% ../../nbs/01_wrds/04_compq.ipynb 7
def default_raw_vars():
    """Defines default variables used in `get_raw_data` if none are specified."""

    return ['datadate', 'gvkey', 'cik', 'cusip', 'fyearq', 'fqtr', 'fyr',
            'sic', 'naics', 'exchg', 'rdq', 'fic',
            'atq', 'req', 'xrdq', 'cheq' ,'saleq','revtq', 'dpq', 'ibq', 'cshoq', 'ceqq', 'seqq', 'txdiq', 'ltq', 
            'txditcq', 'pstkq', 'pstkrq', 'lctq', 'actq', 'piq', 'niq', 'cshprq', 'epsfxq', 
            'opepsq', 'epsfiq' ,'epspiq', 'epspxq' ,'dlttq' ,'dlcq' ,'txtq' ,'xintq' ,'ppegtq' ,
            'ppentq' ,'rectq' ,'invtq' ,'cogsq' ,'xsgaq' ,'ajexq' ,'prccq' ,'capxy' ,'oancfy' ,
            'sstky' ,'prstkcy' ,'dltisy' ,'dltry' ,'dvpq' ,'dvy' ,'sppey' ,'aqcy' , 'fopty', 'scstkcy',
            'wcapq' ,'oibdpq' ,'tstkq' ,'apdedateq' ,'fdateq','cdvcy', 'cheq',
            'intanq','gdwlq','mibq', 'oiadpq','ivaoq','npq','rectrq'
            ]             

# %% ../../nbs/01_wrds/04_compq.ipynb 9
def parse_varlist(vars: List[str]=None,
                  required_vars = [],
                  ) -> str:
    """Figures out which `vars` come from the `{LIBRARY}.{TABLE}` table and which come from the `{LIBRARY}.{COMPANY_TABLE}` table and adds a. and b. prefixes to variable names to feed into an SQL query"""

    # Get all available variables and add suffixes needed for the SQL query
    suffix_mapping = {TABLE: 'a.', COMPANY_TABLE: 'b.', }
    all_avail_vars = list_all_vars().drop_duplicates(subset='name',keep='first').copy()
    all_avail_vars['w_prefix'] = all_avail_vars.apply(lambda row: suffix_mapping[row['wrds_table']] + row['name'] , axis=1)

    if vars == '*': return ','.join(list(all_avail_vars['w_prefix']))
    
    # Add required vars to requested vars
    if vars is None: vars = default_raw_vars()
    vars_to_get =  required_vars + [x for x in list(set(vars)) if x not in required_vars]

    # Validate variables to be downloaded (make sure that they are in the target database)
    invalid_vars = [v for v in vars_to_get if v not in list(all_avail_vars.name)]
    if invalid_vars: raise ValueError(f"These vars are not in the database: {invalid_vars}") 

    # Extract information on which variable comes from which wrds table, so we know what prefix to use
    vars_to_get = pd.DataFrame(vars_to_get, columns=['name'])
    get_these = vars_to_get.merge(all_avail_vars, how = 'left', on = 'name')
        
    return ','.join(list(get_these['w_prefix']))

# %% ../../nbs/01_wrds/04_compq.ipynb 11
def get_raw_data(
        vars: List[str]=None, # If None, downloads `default_raw_vars`; use '*' to get all available variables
        required_vars: List[str]=['gvkey','datadate','fyearq','fqtr','rdq'], #list of variables that will get downloaded, even if not in `vars`
        nrows: int=None, #Number of rows to download. If None, full dataset will be downloaded
        start_date: str=None, # Start date in MM/DD/YYYY format
        end_date: str=None #End date in MM/DD/YYYY format
) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS `{LIBRARY}.{TABLE}` and `{LIBRARY}.{COMPANY_TABLE}`. 
        It also adds `sich` and `naicsh` from the annual table (comp.funda)
    """
 
    wrds_api.validate_dates([start_date, end_date])
    vars = parse_varlist(vars, required_vars=required_vars)

    sql_string=f"""SELECT  {vars}, c.sich, c.naicsh  
                    FROM {LIBRARY}.{TABLE} as a 
                    LEFT JOIN {LIBRARY}.{COMPANY_TABLE} as b ON a.gvkey = b.gvkey
                    LEFT JOIN (
                        SELECT gvkey, fyear, MAX(datadate) as max_date, sich, naicsh
                        FROM comp.funda
                        GROUP BY gvkey, fyear, sich, naicsh
                    ) as c ON a.gvkey = c.gvkey AND a.fyearq = c.fyear
                    WHERE  a.indfmt='INDL' AND a.datafmt='STD' AND a.popsrc='D' AND a.consol='C'
                """
    if start_date is not None: sql_string += r" AND a.datadate >= %(start_date)s"
    if end_date is not None: sql_string += r" AND a.datadate <= %(end_date)s"
    if nrows is not None: sql_string += r" LIMIT %(nrows)s"
    
    return wrds_api.download(sql_string,
                             params={'start_date':start_date, 'end_date':end_date, 'nrows':nrows})

# %% ../../nbs/01_wrds/04_compq.ipynb 17
def process_raw_data(
        df: pd.DataFrame=None,  # Must contain `permno` and `datadate` columns   
        clean_kwargs: dict={},  # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
) -> pd.DataFrame:
    """Drops duplicage, cleans up dates and applies `pandasmore.setup_panel` to `df`"""

    # Drop gvkey-datadate duplicates by retaining the latest fyearq-fqtr combination
    df = df.sort_values(['gvkey','datadate','fyearq','fqtr']).drop_duplicates(subset=['gvkey','datadate'], keep='last').copy()

    # Clean up some useful dates (convert rdq to datetime, and extract the fiscal year end date)
    df['rdq'] = pd.to_datetime(df['rdq'])
    df['dtdate_fiscal'] = pd.to_datetime((df['fyearq'].astype(int).astype(str) + '-' 
                                          + (df['fqtr'].astype(int)*3).astype(str) 
                                          + '-1'), format='%Y-%m-%d'
                                          ) + pd.offsets.MonthEnd(1)
    df['Qdate_fiscal'] = df['dtdate_fiscal'].dt.to_period('Q')

    df = pdm.setup_panel(df, panel_ids=ENTITY_ID_IN_RAW_DSET, time_var=TIME_VAR_IN_RAW_DSET, freq=FREQ, 
                         panel_ids_toint=False,
                         **clean_kwargs)
    return pdm.order_columns(df,['datadate','dtdate','dtdate_fiscal','Qdate_fiscal','fyearq','fqtr','rdq']) 

# %% ../../nbs/01_wrds/04_compq.ipynb 20
def ytd_to_quarterly(df: pd.DataFrame=None, 
                     vars: List[str]=['capxy','oancfy','sstky' ,'prstkcy','dltisy','dltry','dvy','sppey','aqcy','fopty','scstkcy'],
                     suffix: str='_q' # Suffix to add to the new quarterly variables
) -> pd.DataFrame:
    """Convert YTD variables to quarterly variables by taking the difference between the current and previous quarter."""

    out = df.reset_index().set_index(['gvkey','Qdate_fiscal']).sort_index().copy()

    new_vars = []
    for v in vars:
        if v in list(out.columns):  
            new_vars.append(v+suffix)
            out[v+suffix] = np.where(out['fqtr']==1, out[v],out[v] - pdm.lag(out[v]))
        else:
            print(f"Variable {v} not found in the dataset")

    return out.reset_index().set_index(['gvkey','Qdate'])[new_vars].copy()

# %% ../../nbs/01_wrds/04_compq.ipynb 22
def features(df: pd.DataFrame=None
             ) -> pd.DataFrame:
    """Computes a set of features from `df`"""
    
    # convert ytd variables to quarterly
    out = ytd_to_quarterly(df, suffix='_q')

    # industry
    out['sic_full'] = df['sic']
    out['naics_full'] = df['naics']

    # size
    out['stock_price'] = np.abs(df['prccq'])
    out['mktcap'] = out['stock_price'] * df['cshoq']
    out['lag_atq'] = pdm.lag(df['atq'])

    # book equity vars
    out['pstkq0'] = df['pstkq'].fillna(0)
    out['pref_stock'] = np.where(df['pstkrq'].isnull(), out['pstkq0'], df['pstkrq'])
    out['shreq'] = np.where(df['seqq'].isnull(), df['ceqq'] + out['pstkq0'], df['seqq'])
    out['shreq'] = np.where(out['shreq'].isnull(), df['atq'] - df['ltq'], out['shreq'])
    out['bookeq'] = out['shreq'] + df['txditcq'].fillna(0) - out['pref_stock']

    # issuance vars
    out['equityiss_tot'] = (pdm.rdiff(out['bookeq']) - pdm.rdiff(df['req'])) 
    out['equityiss_cfs'] = (out['sstky_q'].fillna(0) - out['prstkcy_q'].fillna(0))
    out['debtiss_tot'] = (pdm.rdiff(df['atq']) - pdm.rdiff(out['bookeq'])) 
    out['debtiss_cfs'] = (out['dltisy_q'].fillna(0) - out['dltry_q'].fillna(0)) 
    out['debtiss_bs'] = (pdm.rdiff(df['dlttq']) + pdm.rdiff(df['dlcq'].fillna(0))) 
    for v in ['equityiss_tot','equityiss_cfs','debtiss_tot','debtiss_cfs','debtiss_bs']:
        out[f'{v}_2la'] = out[v] / out['lag_atq']

    # investment vars
    out['ppent_pch'] = pdm.rpct_change(df['ppentq'])
    out['capx_2la'] = out['capxy_q'] / out['lag_atq']
    out['tobinq'] = (df['atq'] - out['bookeq'] + out['mktcap']) / df['atq']

    # profitability vars
    out['roa'] = df['ibq'] / df['atq']

    # cash flow vars
    out['cflow_is'] = (df['ibq']+df['dpq']) 
    out['cflow_cfs'] = out['oancfy_q'] 
    out['cflow_full'] = np.where(df.dtdate.dt.year<1987, out['cflow_is'], out['cflow_cfs'])
    for v in ['cflow_is','cflow_cfs','cflow_full']:
        out[f'{v}_2la'] = out[v] / out['lag_atq']

    # liquidity vars
    out['cash_2a'] = df['cheq'] / df['atq']

    # leverage vars
    out['booklev'] = (df['dlttq'] + df['dlcq']) / df['atq']
    out.loc[out.booklev<0, 'booklev'] = 0
    out.loc[out.booklev>1, 'booklev'] = 1

    # payout vars
    out['dividends_2la'] = (out['dvy_q'].fillna(0)+df['dvpq'].fillna(0)) / out['lag_atq']
    out['repurchases_2la'] = (out['prstkcy_q'].fillna(0) - pdm.rdiff(df['pstkrq']).fillna(0)) / out['lag_atq']
    
    out = out.replace([np.inf, -np.inf], np.nan)
    return out 
