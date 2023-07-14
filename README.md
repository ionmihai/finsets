# finsets

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

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
