from .resource import readResource
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

    if not hasattr(aqt, "_uuidDict"):
        aqt._uuidDict = {}
    else:
        if uuid in aqt._uuidDict:
            raise RuntimeError(
                f"Duplicate addon UUID {uuid} (previously registered on {aqt._uuidDict[uuid]}"
            )

    aqt._uuidDict[uuid] = __file__


dupUUIDCheck()
