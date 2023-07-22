# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['features_metadata', 'raw_metadata', 'all_metadata']

# %% ../nbs/00_core.ipynb 4
from importlib import import_module
from inspect import signature
import pandas as pd

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
                    if 'return_metadata' in signature(func).parameters: 
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