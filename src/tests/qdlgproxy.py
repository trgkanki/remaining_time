# flake8: noqa

## Prevent import error when running with nosetest

import sys
import os

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from qdlg import *  # NOQA
