from .resource import readResource

uuid = None


def addonUUID():
    global uuid
    if uuid is None:
        uuid = readResource("UUID").strip()
    return uuid
