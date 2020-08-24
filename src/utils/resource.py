# Copyright (C) 2020 Hyun Woo Park
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Note: this function relies that the file exists on 'utils' subdirectory
of the addon!
"""

import os
from aqt import mw


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


def updateMedia(name, newData, replaceExisting=True):
    col = mw.col
    media = col.media
    targetFile = os.path.join(media.dir(), name)

    if os.path.exists(targetFile):
        if not replaceExisting:
            return
        with open(targetFile, "rb") as f:
            if f.read() == newData:
                return  # Identical data already exists
        os.unlink(targetFile)

    col.media.writeData(name, newData)
