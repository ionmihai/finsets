# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/02_papers/hassan_etal_2019.ipynb.

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 4
from __future__ import annotations
import pandas as pd

import pandasmore as pdm
from .. import wrds

# %% auto 0
__all__ = ['source_url', 'variables', 'download', 'clean']

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 5
def source_url():
    """URL where data can be downloaded from. All vintages I downloaded before are included in ascending timeline."""
    
    return pd.Series({'07_08_2023': "https://www.dropbox.com/s/m7o9oycj49rpl9d/firmquarter_2022q1.dta?raw=1"})

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 10
def variables():
    """Names of key variables in the dataset. 
    `company_name`,`hqcountrycode`,`isin`,`cusip`,`ticker` are also available but are omitted here to speed things up and save memory."""
    
    return ['gvkey','date','date_earningscall',
            'PRisk','NPRisk','Risk',
            'PSentiment','NPSentiment','Sentiment',
            'PRiskT_economic','PRiskT_environment','PRiskT_trade','PRiskT_institutions','PRiskT_health','PRiskT_security','PRiskT_tax','PRiskT_technology']

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 12
def download(url: str=source_url()[-1], # URL to the Stata (.dta) version of the dataset
            vars: list=variables(), # Which variables to download
            ) -> pd.DataFrame:
    """Download raw data from `url`"""
    
    return pd.read_stata(url, columns=vars)

# %% ../../nbs/02_papers/hassan_etal_2019.ipynb 16
def clean(df: pd.DataFrame=None, # If None, will download using `download_raw`
          gvkey_permno_link: bool|pd.DataFrame=True, # Whether to download permno or not. If DataFrame, must contain `permno`, `gvkey`, and `Qdate`
          how: str='inner' # How to merge permno into `df` if `gvkey_permno_link` is not False
          ) -> pd.DataFrame:
    """Converts `gvkey` to string and applies `pandasmore.setup_panel`. Adds `permno` if `gvkey_permno_link` is not False."""

    if df is None: df = download()
    else: df = df.copy()
    df['gvkey'] = df['gvkey'].astype('string')
    df = pdm.setup_panel(df, panel_ids='gvkey', time_var='date', freq='Q',
                        panel_ids_toint=False,
                        drop_index_duplicates=True, duplicates_which_keep='last')
    if not gvkey_permno_link: return df
    else:    
      if gvkey_permno_link is True: gvkey_permno_link = wrds.linking.gvkey_permno_q()
      df = df.reset_index().merge(gvkey_permno_link, how=how, on=['gvkey','Qdate'])
      return pdm.setup_panel(df, panel_ids='permno', dates_processed=True, freq='Q',
                              drop_index_duplicates=True, duplicates_which_keep='last')