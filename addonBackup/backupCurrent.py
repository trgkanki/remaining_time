from aqt.utils import showInfo
from aqt import mw

import tarfile
import os

def backupCurrent():
    backupPath = os.path.expanduser('~/addonBackup_backup.tar.xz')
    tar = tarfile.open(backupPath, 'w:xz')
    tar.add(mw.addonManager.addonsFolder(), 'addons21')
    tar.close()
    showInfo(backupPath, title='Use this file if anything goes wrong.')
