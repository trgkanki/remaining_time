from .utils import openChangelog
from .utils import uuid  # duplicate UUID checked here

from .utils.JSEval import execJSFile
from .utils.configrw import getConfig

from aqt.reviewer import Reviewer
from aqt.theme import ThemeManager
from anki.hooks import wrap, addHook

from .mobileSupport.modelModifier import registerMobileScript
from . import jsapi

addHook("profileLoaded", registerMobileScript)


def afterInitWeb(self):
    execJSFile(self.web, "js/main.min.js")


Reviewer._initWeb = wrap(Reviewer._initWeb, afterInitWeb, "after")

# Theme manager


def new_body_class(self, _old):
    showAtBottom = getConfig("showAtBottom", False)
    if showAtBottom:
        rtClass = "remaining-time-bar-bottom"
    else:
        rtClass = "remaining-time-bar-top"

    classes = _old(self)
    return classes + " " + rtClass


ThemeManager.body_class = wrap(ThemeManager.body_class, new_body_class, "around")
