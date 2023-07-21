__version__ = "0.0.2"
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.parent
RESOURCES = PACKAGE_DIR/'resources'

from . import wrds, papers, fred 