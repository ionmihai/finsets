__version__ = "0.0.3"
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent.parent
RESOURCES = PACKAGE_DIR/'resources'

from . import wrds, papers, fred, storage, metadata, dataloader 