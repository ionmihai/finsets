# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/01_wrds/08_mergent.ipynb.

# %% ../../nbs/01_wrds/08_mergent.ipynb 3
from __future__ import annotations
from typing import List

import pandas as pd

from . import wrds_api

# %% auto 0
__all__ = ['PROVIDER', 'URL', 'LIBRARY', 'TABLE', 'ISSUER_TABLE', 'FREQ', 'MIN_YEAR', 'MAX_YEAR', 'ENTITY_ID_IN_RAW_DSET',
           'ENTITY_ID_IN_CLEAN_DSET', 'TIME_VAR_IN_RAW_DSET', 'TIME_VAR_IN_CLEAN_DSET', 'list_all_vars',
           'default_raw_vars', 'parse_varlist', 'get_raw_data', 'process_raw_data']

# %% ../../nbs/01_wrds/08_mergent.ipynb 4
PROVIDER = 'Wharton Research Data Services (WRDS)'
URL = 'https://wrds-www.wharton.upenn.edu/pages/get-data/mergent-fixed-income-securities-database-fisd/'
LIBRARY = 'fisd'
TABLE = 'fisd_mergedissue'
ISSUER_TABLE = 'fisd_mergedissuer'
FREQ = 'D'
MIN_YEAR = 1894
MAX_YEAR = None
ENTITY_ID_IN_RAW_DSET = 'complete_cusip'
ENTITY_ID_IN_CLEAN_DSET = 'cusip'
TIME_VAR_IN_RAW_DSET = 'offering_date'
TIME_VAR_IN_CLEAN_DSET = 'offering_date'

# %% ../../nbs/01_wrds/08_mergent.ipynb 5
def list_all_vars() -> pd.DataFrame:
    "Collects names of all available variables from WRDS f`{LIBRARY}.{TABLE}`."

    try:
        db = wrds_api.Connection()
        issues = db.describe_table(LIBRARY,TABLE).assign(wrds_library=LIBRARY, wrds_table=TABLE)
        issuers = db.describe_table(LIBRARY,ISSUER_TABLE).assign(wrds_library=LIBRARY, wrds_table=ISSUER_TABLE)
    finally:
        db.close()

    return pd.concat([issues, issuers])[['name','type','wrds_library','wrds_table']].copy()

# %% ../../nbs/01_wrds/08_mergent.ipynb 8
def default_raw_vars():
    """Defines default variables used in `get_raw_data` if none are specified."""

    return ['offering_date', 'issue_id', 'issuer_id', 'issuer_cusip', 'issue_cusip', 'complete_cusip', 'isin', 
            'security_level', 'coupon_type', 'convertible', 'foreign_currency', 'rule_144a', 'redeemable', 'bond_type', 
            'maturity', 'coupon', 'offering_amt', 'offering_price', 'principal_amt', 'defaulted',
            'day_count_basis', 'last_interest_date', 'first_interest_date', 'conv_commod_type',
            'cusip_name','naics_code','sic_code', 'treasury_maturity', 'putable',
            'country_domicile',  'private_placement', 'asset_backed', 'interest_frequency','dated_date',
            ]            

# %% ../../nbs/01_wrds/08_mergent.ipynb 10
def parse_varlist(vars: List[str]=None,
                  required_vars = [],
                  ) -> str:
    """Validates that `vars` are available in `{LIBRARY}.{TABLE}` table and adds a. prefixes to variable names to feed into an SQL query"""

    # Get all available variables and add suffixes needed for the SQL query
    suffix_mapping = {TABLE: 'a.', ISSUER_TABLE: 'b.'}
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

# %% ../../nbs/01_wrds/08_mergent.ipynb 12
def get_raw_data(
        vars: List[str]=None, # If None, downloads `default_raw_vars`; use '*' to get all available variables
        required_vars: List[str]=['offering_date','complete_cusip','issuer_id'], #Will get downloaded, even if not in `vars`
        nrows: int=None, #Number of rows to download. If None, full dataset will be downloaded
        start_date: str=None, # Start date in MM/DD/YYYY format
        end_date: str=None #End date in MM/DD/YYYY format
) -> pd.DataFrame:
    """Downloads `vars` from `start_date` to `end_date` from WRDS `{LIBRARY}.{TABLE}` library"""
 
    wrds_api.validate_dates([start_date, end_date])
    vars = parse_varlist(vars, required_vars=required_vars)

    sql_string=f"""SELECT {vars}
                    FROM {LIBRARY}.{TABLE} AS a
                    LEFT JOIN {LIBRARY}.{ISSUER_TABLE} AS b ON a.issuer_id = b.issuer_id
                    WHERE 1=1
                """
    if start_date is not None: sql_string += r" AND offering_date >= %(start_date)s"
    if end_date is not None: sql_string += r" AND offering_date <= %(end_date)s"
    if nrows is not None: sql_string += r" LIMIT %(nrows)s"
    
    return wrds_api.download(sql_string,
                             params={'start_date':start_date, 'end_date':end_date, 'nrows':nrows})

# %% ../../nbs/01_wrds/08_mergent.ipynb 15
def process_raw_data(
        df: pd.DataFrame=None,  # Must contain `permno` and `datadate` columns   
) -> pd.DataFrame:
    """Mainly converts variables to categorical type to save memory."""

    df = df.rename(columns={'complete_cusip':'cusip'})
    to_cat = ['cusip', 'issuer_cusip', 'issue_cusip', 'isin', 'naics_code', 'sic_code', 
           'redeemable', 'security_level', 'country_domicile', 'private_placement', 'foreign_currency', 'rule_144a',
           'asset_backed', 'convertible', 'coupon_type','bond_type']

    for col in to_cat:
        if col in df.columns:
            df[col] = df[col].astype('string').astype('category')

    return df 