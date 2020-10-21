from .resource import getResourcePath
from .JSCallable import JSCallable
from .configrw import getCurrentAddonName, getConfig

from aqt.qt import QAction
from aqt import mw

from datetime import datetime
import subprocess
import os
import platform


logFilePath = getResourcePath("log_%s.log" % getCurrentAddonName())


def isDebugMode(*, _local=[]):
    """ Cached getConfig("debug") """
    if not _local:
        _local.append(getConfig("debug"))
    return _local[0]


def openLogWithPreferredEditor():
    if platform.system() == "Darwin":
        subprocess.call(("open", logFilePath))
    elif platform.system() == "Windows":
        os.startfile(logFilePath)
    else:
        subprocess.call(("xdg-open", logFilePath))


@JSCallable
def log(s: str, *args) -> None:
    if isDebugMode():
        if len(args):
            s = s % args

        now = datetime.now()  # current date and time
        with open(logFilePath, "a", encoding="utf-8") as f:
            f.write("[%s]\t%s\n" % (now.strftime("%Y-%m-%d %H:%M:%S"), s))


def _registerOpenLogMenu():
    if isDebugMode():
        addonName = mw.addonManager.addonName(getCurrentAddonName())
        action = QAction("Show addon log: %s" % addonName, mw)
        action.triggered.connect(openLogWithPreferredEditor)
        mw.form.menuHelp.addAction(action)


_registerOpenLogMenu()
