__version__ = "0.0.3"
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.parent

from . import wrds, papers, fred, fetch_tools
