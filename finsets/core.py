# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% ../nbs/00_core.ipynb 4
from __future__ import annotations
from typing import Literal
from importlib import import_module
from inspect import signature

import pandas as pd
from  thefuzz import process, fuzz

from fastcore.script import call_parse

# %% auto 0
__all__ = ['features_metadata', 'raw_metadata', 'all_metadata', 'search']

# %% ../nbs/00_core.ipynb 5
def features_metadata(submodules: list=['wrds', 'papers'] # list of submodules to collect metadata from
                      ) -> pd.DataFrame:
    "Go through `submodules` of `finsets` and collect metadata from all functions that have `return_metadata` parameter"
    
    df = pd.DataFrame(columns=['name','label','output_of','inputs','inputs_generated_by'])
    for name in submodules:
        module = import_module(f'finsets.{name}')
        for sub in dir(module):
            if sub.startswith('_'): continue
            submodule = import_module(f'finsets.{name}.{sub}')
            for func_name in submodule.__all__:
                func = getattr(submodule, func_name)
                if callable(func):
                    try: 
                        params = signature(func).parameters
                    except:
                        continue
                    if 'return_metadata' in params: 
                        meta = func(return_metadata=True)
                        for var_name in meta['outputs']:
                            for input_name in meta['inputs']:    
                                new_meta = pd.DataFrame({'name':var_name, 
                                                'label':meta['labels'][var_name], 
                                                'output_of':f'{name}.{sub}.{func_name}', 
                                                'inputs':','.join(meta['inputs'][input_name]),
                                                'inputs_generated_by':input_name}, index=[0])
                                df = pd.concat([df,new_meta],ignore_index=True)
    return df

# %% ../nbs/00_core.ipynb 7
def raw_metadata(submodules=['wrds', 'papers'] # list of submodules to collect metadata from
                ) -> pd.DataFrame:
    "Go through `submodules` of `finsets` and collect metadata from `raw_metadata` functions (if present)"

    df = pd.DataFrame(columns=['name','label','output_of','type'])
    for name in submodules:
        module = import_module(f'finsets.{name}')
        for sub in dir(module):
            if sub.startswith('_'): continue
            submodule = import_module(f'finsets.{name}.{sub}')
            if 'raw_metadata' in submodule.__all__:
                df = pd.concat([df,submodule.raw_metadata()],ignore_index=True)
    return df

# %% ../nbs/00_core.ipynb 9
def all_metadata(submodules=['wrds', 'papers'] # list of submodules to collect metadata from
                ) -> pd.DataFrame:
    "Collects `raw_metadata` and `features_metadata` from `submodules` of `finsets`"

    return pd.concat([features_metadata(submodules), raw_metadata(submodules)], ignore_index=True)

# %% ../nbs/00_core.ipynb 11
@call_parse
def search(query: str,              # What to search for 
           which_meta: str='all',   #"all", "features", or "raw"; specifies the function that fetches the metadata you want to search through
           meta_field: str='label', # Which column in the metadata table you want to search through. Use "name" to search variable names.  
           limit: int=10,           # How many results to display                      
           ) -> pd.DataFrame:
    "Search for `query` in metadata returned by f`{meta_func}_metadata`; return `limit` number of results"

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 100)

    try:   
        import finsets
        metadata = getattr(finsets, f'{which_meta}_metadata')()
        results = process.extractBests(query, metadata[meta_field], 
                                        scorer = fuzz.token_sort_ratio,
                                        limit=limit)
        rows = [x[2] for x in results]
        scores = [x[1] for x in results]
        df = metadata.iloc[rows]
        df.index = scores
        df.index.name="SCORE"
        df.columns = df.columns.str.upper()
    finally:
        pd.reset_option('display.max_columns')
        pd.reset_option('display.width')        
    return df
       
