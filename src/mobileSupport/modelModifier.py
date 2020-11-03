import os
import re

from aqt import mw

from .markerReplacer import ReplaceBlock, removeReplaceBlock
from ..utils.resource import readResource, updateMedia
from ..utils.configrw import getConfig

############################# Templates

mediaScriptPath = "_remainingtime.min.js"

scriptBlock = ReplaceBlock(
    "<!-- # 2eecab49dc1f9618 -->",
    "<!-- / 2eecab49dc1f9618 -->",
    f'<script src="{mediaScriptPath}"></script>',
)


def applyScriptBlock(template, key, updated=None):
    orig = template[key]
    fieldUpdated = [False]
    new = scriptBlock.apply(orig, updated=fieldUpdated)
    if fieldUpdated[0]:
        template[key] = new
        if updated:
            updated[0] = True


###################################################################


MODE_SET = "set"
MODE_UNSET = "unset"


def registerMobileScript():
    col = mw.col

    if getConfig("runOnMobile"):
        mode = MODE_SET
        updateMedia(mediaScriptPath, readResource("js/main.min.js").encode("utf-8"))
    else:
        mode = MODE_UNSET
        # Should we remove the media? I don't really think so :(

    updateModels(col, mode)


def updateModels(col, mode):
    models = col.models
    for model in col.models.all():
        templateUpdated = [False]
        for template in model["tmpls"]:
            oldqfmt = template["qfmt"]
            oldafmt = template["afmt"]

            if mode == MODE_SET:
                applyScriptBlock(template, "qfmt")
                if "{{FrontSide}}" not in template["afmt"]:
                    applyScriptBlock(template, "afmt")
                else:
                    template["afmt"] = removeReplaceBlock(
                        template["afmt"], scriptBlock.startMarker, scriptBlock.endMarker
                    )

            else:
                template["qfmt"] = removeReplaceBlock(
                    template["qfmt"], scriptBlock.startMarker, scriptBlock.endMarker
                )
                template["afmt"] = removeReplaceBlock(
                    template["afmt"], scriptBlock.startMarker, scriptBlock.endMarker
                )

            template["qfmt"] = template["qfmt"].replace("\r", "\n")
            template["qfmt"] = re.sub(r"\n{3,}", "\n\n", template["qfmt"])
            template["afmt"] = template["afmt"].replace("\r", "\n")
            template["afmt"] = re.sub(r"\n{3,}", "\n\n", template["afmt"])
            if not (template["qfmt"] == oldqfmt and template["afmt"] == oldafmt):
                templateUpdated[0] = True

        if templateUpdated[0]:
            models.save(model)
