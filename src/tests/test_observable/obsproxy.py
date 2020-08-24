# flake8: noqa

import sys
import os

sys.path.insert(
    1, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../qdlg"))
)

from observable import *  # NOQA
