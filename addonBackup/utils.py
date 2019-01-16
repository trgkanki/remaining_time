from aqt import mw

import json
import os

def deepEqual(a, b):
    """Simple 'deep equal' checker.

    Fuck performance.
    """
    return json.dumps(a) == json.dumps(b)


def getFileModDate(path):
    # Some nefarious addons might wanna copy external file to addon folder
    # in that case st_mtile will hold to the modification date of original
    # file, and we should use st_ctime instead
    try:
        stat = os.stat(path)
        return max(stat.st_mtime, stat.st_ctime)
    except OSError:
        return -1


def getDirectoryRecursiveModTime(dirname):
    mtime = -1
    for (path, _, files) in os.walk(dirname):
        for fname in files:
            fullPath = os.path.join(path, fname)
            try:
                mtime = max(mtime, getFileModDate(fullPath))
            except OSError:
                # sometimes os.stats just fail. Too sad...
                pass

            ext = os.path.splitext(fname)[-1]
            if ext == '.py':
                print("%s/%s" % (path, fname))

    return mtime



# Config related

def getAddonUserConfig(addonID):
    meta = mw.addonManager.addonMeta(addonID)
    return meta.get("config", None)
