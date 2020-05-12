import os

def readResource(filename):
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    inputFilePath = os.path.join(scriptDir, "..", filename)
    with open(inputFilePath, "r", encoding="utf-8") as f:
        return f.read()
