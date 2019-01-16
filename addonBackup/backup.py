from aqt.utils import tooltip
from aqt import mw

import tarfile
import os
import re

from .utils import (
    deepEqual,
    getFileModDate,
    getDirectoryRecursiveModTime
)

from . import globalv
from . import consts
from .utils import getAddonUserConfig


def backupAddonUserData(addonID):
    backupFileName = 'addonBackup_userdata_%s.tar.xz' % addonID
    userDataFolder = os.path.join(mw.addonManager.addonsFolder(addonID), 'user_data')
    userDataBackupPath = os.path.join(mw.col.media.dir(), backupFileName)

    try:
        if os.path.isdir(userDataFolder):
            # Skip backup if it is already up-to-date
            if os.path.exists(userDataBackupPath):
                directoryModTime = getDirectoryRecursiveModTime(userDataFolder)
                backupModTime = getFileModDate(userDataBackupPath)
                if backupModTime >= directoryModTime:
                    return True

            tar = tarfile.open(userDataBackupPath, 'w:xz')
            tar.add(userDataFolder, 'user_data')
            tar.close()
            return True

        else:
            if os.path.exists(userDataBackupPath):
                os.unlink(userDataBackupPath)

            return False

    except OSError:
        tooltip('Backup for user data of addon %s failed' % addonID)
        return False


def backupAddons(self, callback):
    if globalv.noUpload:
        return

    addonIDs = [str(x) for x in mw.addonManager.allAddons()]
    addonIDs = [addonID for addonID in addonIDs
        if addonID not in consts.thisAddonIDs and re.fullmatch(r'\d+', addonID)]

    newConf = {
        'schemaVer': consts.addonSchemaVersion,
        'addons': {
            addonID: {
                'config': getAddonUserConfig(addonID),
                'hasUserData': backupAddonUserData(addonID)
            } for addonID in addonIDs
        }
    }

    # Update only if nesseccary
    if not deepEqual(newConf, mw.col.conf.get(consts.confEntryName, None)):
        mw.col.conf[consts.confEntryName] = newConf
        mw.col.setMod()
