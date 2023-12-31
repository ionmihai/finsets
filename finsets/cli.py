# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/cli.ipynb.

# %% auto 0
__all__ = ['search']

# %% ../nbs/cli.ipynb 2
from fastcore.script import call_parse
from nbdev import nbdev_export
from nbdev.quarto import refresh_quarto_yml, nbdev_readme

# %% ../nbs/cli.ipynb 3
@call_parse
def search(label):
    "Fuzzy search of variable labels for a given string"
    
    from finsets import search
    return search(label)
