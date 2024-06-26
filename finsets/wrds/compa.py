# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/03_compa.ipynb.

# %% ../../nbs/01_wrds/03_compa.ipynb 2
from __future__ import annotations
from typing import List

import pandas as pd
import numpy as np

import pandasmore as pdm
from . import wrds_api

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'LIBRARY', 'TABLE', 'COMPANY_TABLE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET',
           'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'list_all_vars',
           'default_raw_vars', 'parse_varlist', 'get_raw_data', 'process_raw_data', 'features']

# %% ../../nbs/01_wrds/03_compa.ipynb 3
PROVIDER = 'Wharton Research Data Services (WRDS)'
URL = 'https://wrds-www.wharton.upenn.edu/pages/get-data/compustat-capital-iq-standard-poors/compustat/north-america-daily/fundamentals-annual/'
LIBRARY = 'comp'
TABLE = 'funda'
COMPANY_TABLE = 'company' #contains some header information that is missing from comp.funda (e.g. sic and naics) 
FREQ = 'A'
MIN_YEAR = 1950
MAX_YEAR = None
ENTITY_ID_IN_RAW_DSET = 'gvkey'
ENTITY_ID_IN_CLEAN_DSET = 'gvkey'
TIME_VAR_IN_RAW_DSET = 'datadate'
TIME_VAR_IN_CLEAN_DSET = f'{FREQ}date'

# %% ../../nbs/01_wrds/03_compa.ipynb 4
def list_all_vars() -> pd.DataFrame:
    "Collects names of all available variables from WRDS f`{LIBRARY}.{TABLE}` and `{LIBRARY}.{COMPANY_TABLE}`."

    try:
        db = wrds_api.Connection()
        funda = db.describe_table(LIBRARY,TABLE).assign(wrds_library=LIBRARY, wrds_table=TABLE)
        fundn = db.describe_table(LIBRARY,COMPANY_TABLE).assign(wrds_library=LIBRARY, wrds_table=COMPANY_TABLE)
    finally:
        db.close()

    return pd.concat([funda,fundn])[['name','type','wrds_library','wrds_table']].copy()

# %% ../../nbs/01_wrds/03_compa.ipynb 7
def default_raw_vars():
    """Defines default variables used in `get_raw_data` if none are specified."""

    return ['datadate', 'gvkey', 'cusip' ,'cik' ,'tic' ,'fyear' ,'fyr' , 'fic',
            'naicsh', 'sich' , 'sic', 'naics', 'exchg',  
            'lt' ,'at' ,'txditc' ,'pstkl' ,'pstkrv' ,'pstk' ,'csho' ,'ajex' , 'rdip',
            'act' ,'dvc' ,'xad','seq' ,'che' ,'lct' ,'dlc' ,'ib' ,'dvp' ,'txdi' ,'dp' ,
            'txp' ,'oancf' ,'ivncf' ,'fincf' ,'dltt' ,'mib','ceq' ,'invt' ,'cogs' , 'revt',
            'sale' ,'capx' ,'xrd' ,'txdb' ,'prcc_f' ,'sstk' ,'prstkc' ,'dltis' ,'dltr' ,'emp' ,
            'dd1' ,'ppegt' ,'ppent' ,'xint' ,'txt' ,'sppe' ,'gdwl' ,'xrent' ,'re' ,'dvpsx_f' ,
            'tstk' ,'wcap' ,'rect' ,'xsga' ,'aqc' ,'oibdp' ,'dpact','ni' ,'ivao' ,'ivst' ,
            'dv' , 'intan' ,'pi' ,'txfo' ,'pifo' ,'xpp' ,'drc' ,'drlt' ,'ap' ,'xacc' ,'itcb']             

# %% ../../nbs/01_wrds/03_compa.ipynb 9
def parse_varlist(vars: List[str]=None,
                  required_vars = [],
                  ) -> str:
    """Figures out which `vars` come from the `{LIBRARY}.{TABLE}` table and which come from the `{LIBRARY}.{COMPANY_TABLE}` table and adds a. and b. prefixes to variable names to feed into an SQL query"""

    # Get all available variables and add suffixes needed for the SQL query
    suffix_mapping = {TABLE: 'a.', COMPANY_TABLE: 'b.'}
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

# %% ../../nbs/01_wrds/03_compa.ipynb 11
def get_raw_data(
        vars: List[str]=None, # If None, downloads `default_raw_vars`; use '*' to get all available variables
        required_vars: List[str]=['gvkey','datadate'], #list of variables that will get downloaded, even if not in `vars`
        nrows: int=None, #Number of rows to download. If None, full dataset will be downloaded
        start_date: str=None, # Start date in MM/DD/YYYY format
        end_date: str=None #End date in MM/DD/YYYY format
) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS `{LIBRARY}.{TABLE}` library """
 
    wrds_api.validate_dates([start_date, end_date])
    vars = parse_varlist(vars, required_vars=required_vars)

    sql_string=f"""SELECT  {vars}  
                    FROM {LIBRARY}.{TABLE} as a 
                    LEFT JOIN {LIBRARY}.{COMPANY_TABLE} as b ON a.gvkey = b.gvkey
                    WHERE  indfmt='INDL' AND datafmt='STD' AND popsrc='D' AND consol='C'
                """
    if start_date is not None: sql_string += r" AND datadate >= %(start_date)s"
    if end_date is not None: sql_string += r" AND datadate <= %(end_date)s"
    if nrows is not None: sql_string += r" LIMIT %(nrows)s"
    
    return wrds_api.download(sql_string,
                             params={'start_date':start_date, 'end_date':end_date, 'nrows':nrows})

# %% ../../nbs/01_wrds/03_compa.ipynb 19
def process_raw_data(
        df: pd.DataFrame=None,  # Must contain `permno` and `datadate` columns   
        clean_kwargs: dict={},  # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
) -> pd.DataFrame:
    """Applies `pandasmore.setup_panel` to `df`"""

    # Change some variables to categorical
    for col in ['gvkey','naics','sic','fic','cik','tic','cusip']:
        if col in df.columns:
            df[col] = df[col].astype('string').astype('category')

    if 'sich' in df.columns:
        df['sich'] = df['sich'].astype('Int64').astype('string').str.zfill(4).astype('category')

    if 'naicsh' in df.columns:
        df['naicsh'] = df['naicsh'].astype('Int64').astype('string').astype('category')

    # Set up panel structure
    df = pdm.setup_panel(df, panel_ids=ENTITY_ID_IN_RAW_DSET, time_var=TIME_VAR_IN_RAW_DSET, freq=FREQ, 
                         panel_ids_toint=False,
                         **clean_kwargs)
    return df 

# %% ../../nbs/01_wrds/03_compa.ipynb 22
def features(df: pd.DataFrame=None
             ) -> pd.DataFrame:

    out = pd.DataFrame(index=df.index)

    # industry 
    out['sic_full'] = df['sich'].astype('object').fillna(df['sic'].astype('object')).astype('category')
    out['naics_full'] = df['naicsh'].astype('object').fillna(df['naics'].astype('object')).astype('category')

    # size 
    out['stock_price'] = np.abs(df['prcc_f'])
    out['lag_at'] = pdm.lag(df[['at']])
    out['mktcap'] = out['stock_price'] * df['csho']

    # book equity vars
    out['pstk0'] = df['pstk'].fillna(0)
    out['pref_stock'] = np.where(df['pstkrv'].isnull(), df['pstkl'], df['pstkrv'])
    out['pref_stock'] = np.where(out['pref_stock'].isnull(),out['pstk0'], out['pref_stock'])
    out['shreq'] = np.where(df['seq'].isnull(), df['ceq'] + out['pstk0'], df['seq'])
    out['shreq'] = np.where(out['shreq'].isnull(), df['at'] - df['lt'] - df['mib'].fillna(0), out['shreq'])
    out['bookeq'] = out['shreq'] + df['txditc'].fillna(0) + df['itcb'].fillna(0) - out['pref_stock']
    #out['bookeq_w_itcb'] = out['bookeq'] + df['itcb'].fillna(0)

    out['tobinq'] = (df['at'] - out['bookeq'] + out['stock_price'] * df['csho']) / df['at']

    # issuance vars
    out['equityiss_tot'] = (pdm.rdiff(out['bookeq']) - pdm.rdiff(df['re'])) 
    out['equityiss_cfs'] = (df['sstk'].fillna(0) - df['prstkc'].fillna(0))
    out['debtiss_tot'] = (pdm.rdiff(df['at']) - pdm.rdiff(out['bookeq'])) 
    out['debtiss_cfs'] = (df['dltis'].fillna(0) - df['dltr'].fillna(0)) 
    out['debtiss_bs'] = (pdm.rdiff(df['dltt']) + pdm.rdiff(df['dlc'].fillna(0))) 
    for v in ['equityiss_tot','equityiss_cfs','debtiss_tot','debtiss_cfs','debtiss_bs']:
        out[f'{v}_2la'] = out[v] / out['lag_at']

    # investment vars
    out['ppent_pch'] = pdm.rpct_change(df['ppent'])
    out['capx_2la'] = df['capx'] / out['lag_at']

    # profitability vars
    out['roa'] = df['ib'] / df['at']

    # cash flow vars
    out['cflow_is'] = df['ib']+df['dp']
    out['cflow_cfs'] = df['oancf'] 
    out['cflow_full'] = np.where(df.dtdate.dt.year<=1987, out['cflow_is'], out['cflow_cfs'])
    for v in ['cflow_is','cflow_cfs','cflow_full']:
        out[f'{v}_2la'] = out[v] / out['lag_at']

    # liquidity vars
    out['cash_2a'] = df['che'] / df['at']

    # leverage vars
    out['booklev'] = (df['dltt'] + df['dlc']) / df['at']
    out.loc[out.booklev<0, 'booklev'] = 0
    out.loc[out.booklev>1, 'booklev'] = 1

    # payout vars
    out['dividends_2la'] = (df['dvc'].fillna(0) + df['dvp'].fillna(0)) / out['lag_at']
    out['repurchases_2la'] = (df['prstkc'].fillna(0) - pdm.rdiff(df['pstkrv']).fillna(0)) / out['lag_at']

    out = out.replace([np.inf, -np.inf], np.nan)
    return out 

