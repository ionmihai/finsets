# finsets

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

> Download and process datasets commonly used in finance research

Each module handles a different data source. Almost all submodules
(other than utility ones) have a
[`download`](https://ionmihai.github.io/finsets/01_wrds/wrds_api.html#download)
function that downloads the raw data and a
[`clean`](https://ionmihai.github.io/finsets/01_wrds/crspm.html#clean)
function that processes the data into a `pandas.DataFrame` having, as
index, either:

- A `pandas.Period` date reflecting the frequency of the data (for
  time-series datasets), or
- A `pandas.MultiIndex` with a panel identifier in the first dimension
  and a `pandas.Period` date in the second dimension (for panel
  datasets).

The period date in the index will be named following the pattern `Xdate`
where X is the string literal representing the frequency of the data
(e.g. `Mdate` for monthly data, `Qdate` for quarterly data, `Adate` for
annual data).

[Documentation site](https://ionmihai.github.io/finsets/).

[GitHub page](https://github.com/ionmihai/finsets).

## Install

``` sh
pip install finsets
```

## How to use

``` python
import finsets as fds
```

or

``` python
from finsets import fred, wrds, papers
```

Below, we very briefly describe each submodule. For more details, please
see the documentation of each submodule (they provide a lot more
functionality than presented here).

## Core

> Functions that are not specific to a particular data source.

The functions in this model are available directly in the `finsets`
namespace. For example:

``` python
fds.features_metadata()
```

<div>


|     | name          | label                                 | output_of                     | inputs                                            | inputs_generated_by |
|-----|---------------|---------------------------------------|-------------------------------|---------------------------------------------------|---------------------|
| 0   | bookeq        | Book equity                           | wrds.compa.book_equity        | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb       | wrds.compa.clean    |
| 1   | shreq         | Shareholder equity                    | wrds.compa.book_equity        | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb       | wrds.compa.clean    |
| 2   | pref_stock    | Preferred stock                       | wrds.compa.book_equity        | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb       | wrds.compa.clean    |
| 3   | tobinq        | Tobin Q                               | wrds.compa.tobin_q            | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb,pr... | wrds.compa.clean    |
| 4   | equityiss_tot | Equity issuance                       | wrds.compa.issuance_vars      | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb,ss... | wrds.compa.clean    |
| 5   | equityiss_cfs | Equity issuance                       | wrds.compa.issuance_vars      | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb,ss... | wrds.compa.clean    |
| 6   | debtiss_tot   | Debt issuance                         | wrds.compa.issuance_vars      | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb,ss... | wrds.compa.clean    |
| 7   | debtiss_cfs   | Debt issuance                         | wrds.compa.issuance_vars      | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb,ss... | wrds.compa.clean    |
| 8   | debtiss_bs    | Debt issuance                         | wrds.compa.issuance_vars      | at,lt,seq,ceq,txditc,pstk,pstkrv,pstkl,itcb,ss... | wrds.compa.clean    |
| 9   | ppentpch      | Pct change in net PPE                 | wrds.compa.investment_vars    | ppent,capx,at                                     | wrds.compa.clean    |
| 10  | capx2la       | CAPX to lagged assets                 | wrds.compa.investment_vars    | ppent,capx,at                                     | wrds.compa.clean    |
| 11  | roa           | Return on assets                      | wrds.compa.profitability_vars | ib,at                                             | wrds.compa.clean    |
| 12  | cflow2la_is   | Operating cash flows to lagged assets | wrds.compa.cashflow_vars      | dtdate,oancf,ib,dp,at                             | wrds.compa.clean    |
| 13  | cflow2la_cfs  | Operating cash flows to lagged assets | wrds.compa.cashflow_vars      | dtdate,oancf,ib,dp,at                             | wrds.compa.clean    |
| 14  | cflow2la_full | Operating cash flows to lagged assets | wrds.compa.cashflow_vars      | dtdate,oancf,ib,dp,at                             | wrds.compa.clean    |
| 15  | cash2a        | Cash holdings to assets               | wrds.compa.liquidity_vars     | che,at                                            | wrds.compa.clean    |
| 16  | booklev       | Book leverage                         | wrds.compa.leverage_vars      | dltt,dlc,at                                       | wrds.compa.clean    |
| 17  | div2la        | Dividends to lagged assets            | wrds.compa.payout_vars        | dvc,prstkc,at                                     | wrds.compa.clean    |
| 18  | rep2la        | Repurchases to lagged assets          | wrds.compa.payout_vars        | dvc,prstkc,at                                     | wrds.compa.clean    |

</div>

## WRDS

> Downloads and processes datasets from Wharton Research Data Services
> [WRDS](https://wrds-www.wharton.upenn.edu/).

Each WRDS module handles a different library in WRDS (e.g. `compa`
module for the Compustat Annual CCM file, `crspm` for the CRSP Monthly
Stock file, etc.).

Before you use any of the `wrds` modules, you need to create a `pgpass`
with your WRDS credentials. To do that, run

``` python
from finsets.wrds import wrds_api
```

``` python
db = wrds_api.Connection()
```

    WRDS recommends setting up a .pgpass file.
    You can create this file yourself at any time with the create_pgpass_file() function.
    Loading library list...
    Done

This will prompt you for your WRDS username and password. After you
enter your credentials, if you don’t have a `pgpass` file already set
up, it will ask you if you want to do that. Hit `y` and it will be
automatically created for you. After this, you will never have to input
your WRDS password.

You will still have to supply your WRDS username to functions that
retrieve data from WRDS (all of them have a `wrds_username` parameter).
If you don’t want to be prompted for the username for every download,
save it under a `WRDS_USERNAME` environment variable:

- On Windows, in a Command Prompt:
  - `setx WRDS_USERNAME "your_wrds_username_here"`
- On Linux, in a terminal:
  - `echo 'export WRDS_USERNAME="your_wrds_username_here"' >> ~/.bashrc && source ~/.bashrc`
- On macOS, since macOS Catalina:
  - `echo 'export WRDS_USERNAME="your_wrds_username_here"' >> ~/.zshrc && source ~/.szhrc`
- On macOS, prior to macOS Catalina:
  - `echo 'export WRDS_USERNAME="your_wrds_username_here"' >> ~/.bash_profile && source ~/.bash_profile`

The functions in the `wrds_` modules will close database connections to
WRDS automatically. However, if you open a connection manually, as above
(with `wrds.Connection()`) make sure you remember to close that
connection. In our example above:

``` python
db.close()
```

Check the `wrds_utils` module for an introduction to some of the main
utilities that come with the `wrds` package.

## FRED

> Downloads and processes datasets from the St. Louis
> [FRED](https://fred.stlouisfed.org/).

To use the functions in the `fred` module, you’ll need an API key from
the St. Louis FRED.

Get one [here](https://fred.stlouisfed.org/docs/api/api_key.html) and
store it in your environment variables under the name `FRED_API_KEY`

Alternatively, you can supply the API key directly as the `api_key`
parameter in each function in the `fred` module.

``` python
fred.clean('GDP', label='Nominal GDP').tail()
```

<div>


|        | dtdate     | Nominal GDP |
|--------|------------|-------------|
| Qdate  |            |             |
| 2022Q1 | 2022-01-01 | 24740.480   |
| 2022Q2 | 2022-04-01 | 25248.476   |
| 2022Q3 | 2022-07-01 | 25723.941   |
| 2022Q4 | 2022-10-01 | 26137.992   |
| 2023Q1 | 2023-01-01 | 26529.774   |

</div>

## PAPERS

> Downloads and processes datasets made available by the authors of
> academic papers.

Each `papers` module handles a different paper. The naming convention is
that the module’s name is made up of the last names of the authors and
the publication year, separated by underscores. If more than two
authors, all but the first author’s name is replaced by ‘etal’. For
example, the module for the paper “Firm-Level Political Risk:
Measurement and Effects” (2019) by Tarek A. Hassan, Stephan Hollander,
Laurence van Lent, Ahmed Tahoun is named `hasan_etal_2019`.

``` python
papers.hassan_etal_2019.variables()[:7]
```

    ['gvkey', 'date', 'date_earningscall', 'PRisk', 'NPRisk', 'Risk', 'PSentiment']
