# finsets

<!-- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT! -->

Please visit the [documentation
site](https://ionmihai.github.io/finsets/).

The GitHub page is [here](https://github.com/ionmihai/finsets).

## Install

``` sh
pip install finsets
```

## How to use

``` python
import finsets as fds
from finsets import wrds2 as wrds
```

## WRDS

Before you use any of the `wrds_` modules, you need to create a `pgpass`
with your WRDS credentials. To do that, run

``` python
db = wrds.Connection()
```

This will prompt you for your WRDS username and password. After you
enter your credentials, if you don’t have a `pgpass` file already set
up, it will ask you if you want to do that. Hit `y` and it will be
automatically created for you. After this, you will never have to input
your WRDS password.

You will still have to supply your WRDS username to functions that
retrieve data from WRDS (all of them have a `wrds_username` parameter).
If you don’t want to be prompted for the username for every download,
save it under a `WRDS_USERNAME` environment variable: - On Windows, in a
Command Prompt: - `setx WRDS_USERNAME "your_wrds_username_here"` - On
Linux, in a terminal: -
`echo 'export WRDS_USERNAME="your_wrds_username_here"' >> ~/.bashrc && source ~/.bashrc` -
On macOS, since macOS Catalina: -
`echo 'export WRDS_USERNAME="your_wrds_username_here"' >> ~/.zshrc && source ~/.szhrc` -
On macOS, prior to macOS Catalina: -
`echo 'export WRDS_USERNAME="your_wrds_username_here"' >> ~/.bash_profile && source ~/.bash_profile`

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

To use the functions in the `fred` module, you’ll need an API key from
the St. Louis FRED.

Get one [here](https://fred.stlouisfed.org/docs/api/api_key.html) and
store it in your environment variables under the name `FRED_API_KEY`

Alternatively, you can supply the API key directly as the `api_key`
parameter in each function in the `fred` module.
