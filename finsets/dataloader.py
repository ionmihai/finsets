# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_dataloader.ipynb.

# %% auto 0
__all__ = ['fetch', 'get_text_file_from_url', 'batch_download']

# %% ../nbs/02_dataloader.ipynb 3
import requests
from io import StringIO
from importlib import import_module

import pandas as pd

from .storage import BaseStorage

# %% ../nbs/02_dataloader.ipynb 5
def fetch(dataset_name: str=None, # Name of dataset we want to retrieve
          finsets_module: str=None, # Which finsets module creates the dataset we want
          storage: BaseStorage=None, # Storage object indicating where the data should be retrieved from / saved to
          func: str='clean', # function inside `finsets_module` that retrieves the data you want. e.g. 'download' or 'clean'
          force_fetch: bool=False # Whether to redownload/reprocess the dataset even if it exists in storage
          ):

    if storage.exists(dataset_name) and (not storage.is_stale(dataset_name)) and (not force_fetch):
        df = storage.load(dataset_name)
    else:
        module = import_module(finsets_module)
        df = getattr(module, func)
        storage.save(df, dataset_name)

    return df

# %% ../nbs/02_dataloader.ipynb 8
def get_text_file_from_url (url, #Data at this url must be readable with pandas.read_csv
             nrows: int=None, #Get only the first `nrows` from the file. If None, gets the entire file
             delimiter: str=',',
             **pd_read_csv_kwargs,
    ) -> pd.DataFrame:
    "Gets the first `nrows` from the file found at `url`. Data at `url` must be separated by `delimiter` and be readable by pandas.read_csv"
    
    if nrows is not None:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        lines = []
        for i, line in enumerate(response.iter_lines(decode_unicode=True)):
            if i >= nrows: break
            lines.append(line)
        partial_csv = '\n'.join(lines)

        return pd.read_csv(StringIO(partial_csv), delimiter=delimiter, **pd_read_csv_kwargs)

    return pd.read_csv(url, delimiter=delimiter,  **pd_read_csv_kwargs)


# %% ../nbs/02_dataloader.ipynb 11
def batch_download():
    pass 
