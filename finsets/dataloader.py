# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_dataloader.ipynb.

# %% auto 0
__all__ = ['get_text_file_from_url', 'batch_download']

# %% ../nbs/02_dataloader.ipynb 3
import requests
from io import StringIO

import pandas as pd

# %% ../nbs/02_dataloader.ipynb 5
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


# %% ../nbs/02_dataloader.ipynb 8
def batch_download():
    pass 
