from .resource import readResource
from .configrw import getCurrentAddonName
import aqt

_uuid = None


def addonUUID():
    global _uuid
    if _uuid is None:
        _uuid = readResource("UUID").strip()

    return _uuid


def dupUUIDCheck():
    """ Check for duplicate UUID and raise exception if one exists """
    uuid = addonUUID()

    if (
        uuid == "aceb54e9-1323-49aa-9644-cf0a28a3d0c3"
        and getCurrentAddonName() != "addon_template"
    ):
        raise RuntimeError("Assign new UUID to addon %s" % getCurrentAddonName())

    if not hasattr(aqt, "_uuidDict"):
        aqt._uuidDict = {}
    else:
        if uuid in aqt._uuidDict:
            raise RuntimeError(
                f"Duplicate addon UUID {uuid} (previously registered on {aqt._uuidDict[uuid]}"
            )

    aqt._uuidDict[uuid] = __file__


dupUUIDCheck()
