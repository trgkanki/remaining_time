from aqt.utils import showInfo, askUser
from aqt import mw

from . import globalv
from . import consts
from .backupCurrent import backupCurrent
from .utils import getAddonUserConfig, deepEqual

import os

import tarfile

noUpload = False
noUploadAsked = False
class AbortSyncException(Exception):
    pass

def askNoUpload():
    global noUploadAsked
    if noUploadAsked:
        return
    noUploadAsked = True

    if askUser('Preserve current addon backup? (Selecting "No" means wiping your current backup)'):
        globalv.noUpload = True

def migrateSchema(config):
    raise NotImplementedError('Not implemented')


def applyAddonBackup(self, callback):

    addonBackupConfig = mw.col.conf.get(consts.confEntryName, None)
    if addonBackupConfig is None:
        showInfo('''\
[addonBackup] READ CAREFULLY
[addonBackup] READ CAREFULLY

No backup data available at your PC. This means either...
- You've first installed this addon. Welcome! Press NO at the next window. (You won't have 'current' backup apparently.)
- You have a backup at AnkiWeb, but they aren't synced with you PC yet. Press YES at the next window, sync to AnkiWeb, then restart Anki.
- In other cases, please file an issue on https://github.com/phu54321/anki_plugins/

Thanks for using addonBackup!
''')
        askNoUpload()
        return

    if addonBackupConfig['schemaVer'] < consts.addonSchemaVersion:
        addonBackupConfig = migrateSchema(addonBackupConfig)


    _settingChanged = False

    def askSettingChange():
        nonlocal _settingChanged
        if _settingChanged:
            return


        if not askUser('[addonBackup] Backup found. Download from backup? (Anki restart needed)'):
            raise AbortSyncException()

        _settingChanged = True
        backupCurrent()

    try:
        installedAddonIDs = mw.addonManager.allAddons()
        
        # Install missing addons
        for addonID, metadata in addonBackupConfig['addons'].items():
            if addonID not in installedAddonIDs:
                askSettingChange()
                _, errs = mw.addonManager.downloadIds([addonID])
                if errs:
                    showInfo('Download of addon %s failed. Check internet connection' % addonID)
                    askNoUpload()
                    continue

                if metadata['hasUserData'] and not canUnpackAddonsUserdata(addonID):
                    showInfo('Backup had user data of addon %s, but it is not found in media folder (Not properly synced?)\n' +
                        'addonBackup won\'t sync addon settings. Try restarting anki after syncing your media.' % addonID)
                    askNoUpload()
                    continue

                savedConfig = metadata['config']
                if savedConfig:
                    mw.addonManager.writeConfig(addonID, savedConfig)

                if metadata['hasUserData']:
                    unpackAddonUserData(addonID)

                globalv.noUpload = True

            else:
                savedConfig = metadata['config']
                currentConfig = getAddonUserConfig(addonID)
                if savedConfig and not deepEqual(currentConfig, savedConfig):
                    if metadata['hasUserData'] and not canUnpackAddonsUserdata(addonID):
                        showInfo('Backup had user data of addon %s, but it is not found in media folder (Not properly synced?)\n' +
                            'addonBackup won\'t sync addon configuration. Try restarting anki after syncing your media.' % addonID)
                        askNoUpload()
                        continue

                    askSettingChange()

                    mw.addonManager.writeConfig(addonID, savedConfig)
                    if metadata['hasUserData']:
                        unpackAddonUserData(addonID)

                    globalv.noUpload = True

        # Don't delete excess addons by default
        if _settingChanged:
            showInfo('Addons updated. Restart anki.', title='Restart required')

    except AbortSyncException:
        askNoUpload()



def canUnpackAddonsUserdata(addonID):
    backupFileName = 'addonBackup_userdata_%s.tar.xz' % addonID
    userDataBackupPath = os.path.join(mw.col.media.dir(), backupFileName)
    return os.path.exists(userDataBackupPath)

def unpackAddonUserData(addonID):
    backupFileName = 'addonBackup_userdata_%s.tar.xz' % addonID
    userDataBackupPath = os.path.join(mw.col.media.dir(), backupFileName)

    try:
        tar = tarfile.open(userDataBackupPath, 'r:xz')
        tar.extractall(mw.addonManager.addonsFolder(addonID))
        tar.close()

    except OSError:
        showInfo('Cannot extract user_data for addon %s' % addonID)
        pass
