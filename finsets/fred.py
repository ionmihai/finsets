# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/fred.ipynb.

# %% ../nbs/fred.ipynb 3
from __future__ import annotations
from typing import List, Dict, Tuple, Callable
import os

import pandas as pd
import numpy as np
from .fredapi2 import Fred

import pandasmore as pdm

# %% auto 0
__all__ = ['get_series', 'get_series_info', 'search', 'common_raw_vars']

# %% ../nbs/fred.ipynb 4
def get_series(series: str=None, # FRED series name
               label: str=None, # Name you want to give to the series in the output DataFrame. If None, use lowercase of `series`
               api_key: str=None # FRED api key. If None, will use os.getenv("FRED_API_KEY")
               ) -> pd.DataFrame: 
    """Retrieves series from FRED, cleans the date and sets it as index"""

    if api_key is None: api_key = os.getenv("FRED_API_KEY")
    api = Fred(api_key=api_key)
    freq = api.get_series_info('GDP').frequency_short 
    if label is None: label = str.lower(series)
    df = api.get_series(series).to_frame(name=label).reset_index().rename({'index':'date'},axis=1)
    df = pdm.setup_tseries(df, freq=freq).drop('date', axis=1)
    return df 

# %% ../nbs/fred.ipynb 6
def get_series_info(series: str=None, # FRED series name
                    api_key: str=None # FRED api key. If None, will use os.getenv("FRED_API_KEY")
                    ) -> pd.Series:
    """Get metadata for given `series` from FRED"""

    if api_key is None: api_key = os.getenv("FRED_API_KEY")
    api = Fred(api_key=api_key)
    return api.get_series_info(series)

# %% ../nbs/fred.ipynb 8
def search(search_text: str=None, # What to search for
              nr_results: int=5, # How many results to output
              api_key: str=None # FRED api key. If None, will use os.getenv("FRED_API_KEY")
              ) -> pd.DataFrame:
    """Get metadata for given `series` from FRED"""

    if api_key is None: api_key = os.getenv("FRED_API_KEY")
    api = Fred(api_key=api_key)  
    return api.search(search_text)\
              .assign(popularity = lambda x: x.popularity.astype('Int64'))\
              .sort_values('popularity', ascending=False)\
              .pipe(pdm.order_columns, ['title', 'popularity','frequency_short', 'observation_start', 'observation_end'])\
              .iloc[:nr_results]

# %% ../nbs/fred.ipynb 10
def common_raw_vars() -> pd.DataFrame:
    """List of FRED series commonly used in finance research"""

    vars = [
    ['TB3MS','yield_3mt','3-month treasury bill secondary market rate', 'M', 'NSA',1934],
    ['DTB3','yield_3mt','3-month treasury bill secondary market rate', 'D', 'NSA',1954],
    ['GS10','yield_10yt','10-year treasury constant maturity market yield', 'M', 'NSA',1953],
    ['DGS10','yield_10yt', '10-year treasury constant maturity market yield', 'D', 'NSA',1962],
    ['GS1','yield_1yt', '1-year treasury constant maturity market yield', 'M', 'NSA', 1953],
    ['DGS1','yield_1yt', '1-year treasury constant maturity market yield', 'D', 'NSA', 1962],
    ['AAA','yield_aaa', 'Moodys Aaa seasoned corporate bond yield', 'M', 'NSA', 1919], 
    ['BAA','yield_baa', 'Moodys Baa seasoned corporate bond yield', 'M', 'NSA', 1919], 
    ['DAAA','yield_aaa', 'Moodys Aaa seasoned corporate bond yield', 'D', 'NSA', 1983], 
    ['DBAA','yield_baa', 'Moodys Baa seasoned corporate bond yield', 'D', 'NSA', 1986],     
    ['FEDFUNDS','yield_fedf', 'federal funds effective rate', 'M', 'NSA', 1954], 
    ['DFF','yield_fedf', 'federal funds effective rate', 'D', 'NSA', 1954], 
    ['CPIAUCSL','cpi', 'cpi all urban consumers', 'M', 'SA', 1947],  
    ['CPIAUCNS','cpi', 'cpi all urban consumers', 'M', 'NSA', 1913],  
    ['INDPRO','indprod', 'industrial production', 'M', 'SA', 1919],
    ['IPB50001SQ','indprod', 'industrial production', 'Q', 'SA', 1919],
    ['UNRATE','unemp', 'unemployment rate', 'M', 'SA', 1948], 
    ['GDP','ngdp', 'nominal gdp','Q','SA',1947],
    ['GDPC1','rgdp', 'real gdp','Q','SA',1947],
    ['GNP','ngnp', 'nominal gnp','Q','SA',1947],
    ['GNPC96','rgnp', 'real gnp','Q','SA',1947],
    ['GDPPOT','pot_rgdp','real potential gdp','Q','SA',1949],
    ['USREC','rec_dum', 'nber recession indicator', 'M', 'NSA', 1854], 
    ['RECPROUSM156N','rec_prob', 'nber real time recession probability', 'M', 'NSA', 1967],
    ['CFNAI','cfnai','chicago fed national activity index','M','NSA',1967],
    ['UMCSENT','sent_mich','U Michigan consumer confidence index','M','NSA',1977],
    ['MICH','exp_inflation','U Michigan inflation expectation','M','NSA',1978],
    ['USEPUINDXM','pu_bbd','overall EPU index from Baker,Bloom,Davis','M', 'NSA',1985],
    ['USEPUNEWSINDXM','punews_bbd','news comp of EPU index from BBD','M', 'NSA',1985],
    ['USEPUINDXD','pu_bbd','D EPU from BBD','D','NSA',1985],
    ['VIXCLS','vix','VIX index on snp100 from CBOE 1month','D','NSA',1990],
    ['VXOCLS','vxo','VXO index on snp500 from CBOE','D','NSA',1986]
    ]
    return pd.DataFrame(data = vars, columns = ['id','label','desc','freq','season_adj','starts']) 

