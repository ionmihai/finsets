# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/wrds_compa.ipynb.

# %% auto 0
__all__ = ['default_raw_vars', 'download', 'clean', 'book_equity', 'investment_vars', 'profitability_vars', 'cashflow_vars',
           'liquidity_vars', 'leverage_vars', 'payout_vars', 'value_vars', 'issuance_vars']

# %% ../nbs/wrds_compa.ipynb 3
from typing import List

import pandas as pd
import numpy as np

import pandasmore as pdm
from . import wrds_utils
from . import wrds2 as wrds  

# %% ../nbs/wrds_compa.ipynb 4
def default_raw_vars():
    """Default variables used in `download` if none are specified. Takes about 2 min to download."""

    return ['datadate', 'gvkey', 'cusip' ,'cik' ,'tic' ,'fyear' ,'fyr' ,'naicsh', 'sich' ,'exchg',  
            'lt' ,'at' ,'txditc' ,'pstkl' ,'pstkrv' ,'pstk' ,'csho' ,'ajex' , 'rdip',
            'act' ,'dvc' ,'xad','seq' ,'che' ,'lct' ,'dlc' ,'ib' ,'dvp' ,'txdi' ,'dp' ,
            'txp' ,'oancf' ,'ivncf' ,'fincf' ,'dltt' ,'mib','ceq' ,'invt' ,'cogs' , 'revt',
            'sale' ,'capx' ,'xrd' ,'txdb' ,'prcc_f' ,'sstk' ,'prstkc' ,'dltis' ,'dltr' ,'emp' ,
            'dd1' ,'ppegt' ,'ppent' ,'xint' ,'txt' ,'sppe' ,'gdwl' ,'xrent' ,'re' ,'dvpsx_f' ,
            'tstk' ,'wcap' ,'rect' ,'xsga' ,'aqc' ,'oibdp' ,'dpact' ,'fic' ,'ni' ,'ivao' ,'ivst' ,
            'dv' , 'intan' ,'pi' ,'txfo' ,'pifo' ,'xpp' ,'drc' ,'drlt' ,'ap' ,'xacc' ,'itcb']             

# %% ../nbs/wrds_compa.ipynb 6
def download(vars: List[str]=None, # If None, downloads `default_raw_vars`; else `permno`, `permco`, and `date` are added by default
             wrds_username: str=None, #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
             start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
             end_date: str=None #End date in MM/DD/YYYY format; if None, defaults to current date
             ) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS comp.funda library and adds PERMNO and PERMCO as in CCM"""

    if vars is None: vars = default_raw_vars()
    vars = ','.join(['a.gvkey', 'a.datadate'] + 
                    [f'a.{x}' for x in vars if x not in ['datadate', 'gvkey']])

    sql_string=f"""SELECT b.lpermno as permno, b.lpermco as permco, b.liid as iid, {vars}
                    FROM comp.funda AS a
                    INNER JOIN crsp.ccmxpf_lnkhist AS b ON a.gvkey = b.gvkey
                    WHERE datadate BETWEEN b.linkdt AND COALESCE(b.linkenddt, CURRENT_DATE)
                            AND b.linktype IN ('LU','LC') AND b.linkprim IN ('P','C')
                            AND indfmt='INDL' AND datafmt='STD' AND popsrc='D' AND consol='C'
                            AND datadate BETWEEN '{start_date}' AND COALESCE(%(end)s, CURRENT_DATE)
                """
    return wrds_utils.download(sql_string, wrds_username=wrds_username, params={'end':end_date})

# %% ../nbs/wrds_compa.ipynb 9
def clean(df: pd.DataFrame=None, # If None, downloads `vars` using `download` function; else, must contain `permno` and `datadate` columns
          vars: List[str]=None, # If None, downloads `default_raw_vars`
          wrds_username: str=None, #If None, looks for WRDS_USERNAME with `os.getenv`, then prompts you if needed
          start_date: str="01/01/1900", # Start date in MM/DD/YYYY format
          end_date: str=None, # End date. Default is current date          
          clean_kwargs: dict={}, # Params to pass to `pdm.setup_panel` other than `panel_ids`, `time_var`, and `freq`
          ) -> pd.DataFrame:
    """Applies `pandasmore.setup_panel` to `df`. If `df` is None, downloads `vars` using `download` function."""

    if df is None: df = download(vars=vars, wrds_username=wrds_username, start_date=start_date, end_date=end_date)
    df = pdm.setup_panel(df, panel_ids='permno', time_var='datadate', freq='Y', **clean_kwargs)
    return df 

# %% ../nbs/wrds_compa.ipynb 12
def book_equity(df: pd.DataFrame=None, # If None, downloads (and cleans) only required vars
                add_itcb=False,
                list_reqs: bool=False # If true, just returns a list of the required variables
                ) -> pd.DataFrame:

    reqs = ['at', 'lt', 'seq', 'ceq', 'txditc', 'pstk', 'pstkrv', 'pstkl', 'itcb']
    if list_reqs: return reqs
    if df is None: df = clean(download_vars=reqs)
    df = df[reqs].copy()

    df['pstk'] = df['pstk'].fillna(0)
    df['pref_stock'] = np.where(df['pstkrv'].isnull(), df['pstkl'], df['pstkrv'])
    df['pref_stock'] = np.where(df['pref_stock'].isnull(),df['pstk'], df['pref_stock'])

    df['shreq'] = np.where(df['seq'].isnull(), df['ceq'] + df['pstk'], df['seq'])
    df['shreq'] = np.where(df['shreq'].isnull(), df['at'] - df['lt'], df['shreq'])

    df['bookeq'] = df['shreq'] + df['txditc'].fillna(0) - df['pref_stock']
    if add_itcb: df['bookeq'] = df['bookeq'] + df['itcb'].fillna(0)
    
    return df[['bookeq','shreq','pref_stock']].copy()

# %% ../nbs/wrds_compa.ipynb 18
def investment_vars(df: pd.DataFrame=None, # If None, downloads (and cleans) only required vars 
                    list_reqs: bool=False # If true, just returns a list of the required variables
                    ) -> pd.DataFrame:
    
    reqs = ['ppent','capx','at']
    if list_reqs: return reqs
    df = df[reqs].copy()

    df['ppentpch'] = pdm.rpct_change(df['ppent'])
    df['capx2la'] = df['capx'] / pdm.lag(df['at'])

    return df[['ppentpch','capx2la']].copy()

# %% ../nbs/wrds_compa.ipynb 21
def profitability_vars(df: pd.DataFrame, 
                    list_reqs: bool=False # If true, just returns a list of the required variables
                    ) -> pd.DataFrame:
    
    reqs = ['ib','at']
    if list_reqs: return reqs
    df = df[reqs].copy()

    df['roa'] = df['ib'] / df['at']

    return df[['roa']].copy()

# %% ../nbs/wrds_compa.ipynb 24
def cashflow_vars(df: pd.DataFrame, 
                    list_reqs: bool=False # If true, just returns a list of the required variables
                    ) -> pd.DataFrame:
    
    reqs = ['dtdate','oancf','ib','dp','at']
    if list_reqs: return reqs
    df = df[reqs].copy()

    df['cflow2la_is'] = (df['ib']+df['dp']) / pdm.lag(df['at'])
    df['cflow2la_cfs'] = df['oancf'] / pdm.lag(df['at'])
    df['cflow2la_full'] = np.where(df.dtdate.dt.year<1987, df['cflow2la_is'], df['cflow2la_cfs'])
    
    return df[['cflow2la_is', 'cflow2la_cfs', 'cflow2la_full']].copy()

# %% ../nbs/wrds_compa.ipynb 27
def liquidity_vars(df: pd.DataFrame, 
                    list_reqs: bool=False # If true, just returns a list of the required variables
                    ) -> pd.DataFrame:
    
    reqs = ['che','at']
    if list_reqs: return reqs
    df = df[reqs].copy()

    df['cash2a'] = df['che'] / df['at']

    return df[['cash2a']].copy()

# %% ../nbs/wrds_compa.ipynb 30
def leverage_vars(df: pd.DataFrame, 
                    list_reqs: bool=False # If true, just returns a list of the required variables
                    ) -> pd.DataFrame:
    
    reqs = ['dltt','dlc','at']
    if list_reqs: return reqs
    df = df[reqs].copy()

    df['booklev'] = (df['dltt'] + df['dlc']) / df['at']
    df.loc[df.booklev<0, 'booklev'] = 0
    df.loc[df.booklev>1, 'booklev'] = 1
        
    return df[['booklev']].copy()

# %% ../nbs/wrds_compa.ipynb 33
def payout_vars(df: pd.DataFrame, 
                    list_reqs: bool=False # If true, just returns a list of the required variables
                    ) -> pd.DataFrame:
    
    reqs = ['dvc','prstkc','at']
    if list_reqs: return reqs
    df = df[reqs].copy()

    df['div2la'] = df['dvc'].fillna(0) / pdm.lag(df['at'])
    df['rep2la'] = df['prstkc'].fillna(0) / pdm.lag(df['at'])

    return df[['div2la','rep2la']].copy()

# %% ../nbs/wrds_compa.ipynb 36
def value_vars(df: pd.DataFrame, 
                list_reqs: bool=False # If true, just returns a list of the required variables
                ) -> pd.DataFrame:
    
    reqs = ['at','prcc_f','csho'] + [x for x in book_equity(list_reqs=True) if x not in ['at','prcc_f','csho']]
    if list_reqs: return reqs
    df = df[reqs].copy()

    beq = book_equity(df)[['bookeq']].copy()
    df = df.join(beq)

    df['tobinq'] = (df['at'] - df['bookeq'] + df['prcc_f'] * df['csho']) / df['at']

    return  df[['tobinq']].copy()

# %% ../nbs/wrds_compa.ipynb 39
def issuance_vars(df: pd.DataFrame, 
                list_reqs: bool=False # If true, just returns a list of the required variables
                ) -> pd.DataFrame:
    
    reqs_subset = ['at','sstk','prstkc','dltis','dltr', 're', 'dlc','dltt']
    reqs = reqs_subset + [x for x in book_equity(list_reqs=True) if x not in reqs_subset]
    if list_reqs: return reqs
    df = df[reqs].copy()

    beq = book_equity(df)[['bookeq']].copy()
    df = df.join(beq)
    
    df['lag_at'] = pdm.lag(df['at'])

    df['equityiss_cfs'] = (df['sstk'].fillna(0) - df['prstkc'].fillna(0)) / df['lag_at']
    df['debtiss_cfs'] = (df['dltis'].fillna(0) - df['dltr'].fillna(0)) / df['lag_at']

    df['debtiss_bs'] = (pdm.rdiff(df['dltt']) + pdm.rdiff(df['dlc'].fillna(0))) / df['lag_at']

    df['equityiss_tot'] = (pdm.rdiff(df['bookeq']) - pdm.rdiff(df['re'])) / df['lag_at']
    df['debtiss_tot'] = (pdm.rdiff(df['at']) - pdm.rdiff(df['bookeq'])) / df['lag_at']

    return df[['equityiss_tot','equityiss_cfs', 'debtiss_tot', 'debtiss_cfs', 'debtiss_bs']].copy()
