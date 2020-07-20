"""
Note: this function relies that the file exists on 'utils' subdirectory
of the addon!
"""

import os


def getResourcePath(filename):
    if os.path.isabs(filename):
        return filename

    scriptDir = os.path.dirname(os.path.realpath(__file__))
    inputFilePath = os.path.join(scriptDir, "..", filename)
    return os.path.abspath(inputFilePath)


def readResource(filename, binary=False):
    inputFilePath = getResourcePath(filename)

    if binary:
        with open(inputFilePath, "rb") as f:
            return f.read()

    else:
        with open(inputFilePath, "r", encoding="utf-8") as f:
            return f.read()
