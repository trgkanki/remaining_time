// Copyright (C) 2020 Hyun Woo Park
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

import { requestJSONP } from './jsonp'

/**
 * Retrieve addon config set on Anki side. Python side uploads addon config to
 * user's media folder.
 */
export async function getAddonConfig (key?: string): Promise<any> {
  // Due to CORB, we cannot use `.json` as file extension.
  const jsURL = `_addon_config_${ADDON_UUID.replace(/-/g, '_')}.js`
  const callbackName = `_ADDON_CONFIG_CALLBACK_${ADDON_UUID.replace(/-/g, '')}`
  const res = await requestJSONP(jsURL, callbackName)
  if (key) return res[key]
  else return res
}
