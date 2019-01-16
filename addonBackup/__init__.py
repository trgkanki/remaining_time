from anki.hooks import wrap
from aqt.main import AnkiQt

from .backup import backupAddons
from .unpack import applyAddonBackup


AnkiQt.unloadCollection = wrap(AnkiQt.unloadCollection, backupAddons, 'before')
AnkiQt.loadProfile = wrap(AnkiQt.loadProfile, applyAddonBackup, 'after')
