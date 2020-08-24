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
