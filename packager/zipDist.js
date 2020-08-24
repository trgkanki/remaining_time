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

const NodeZip = require('node-zip')
const walk = require('walkdir')
const fs = require('fs')
const path = require('path')

const ignoreList = [
  '__pycache__',
  'meta.json',
  'tests'
]

exports.zipDist = function (destination) {
  const zip = new NodeZip()
  const paths = walk.sync('src')
  for (const fPath of paths) {
    let ignore = false
    for (const pattern of ignoreList) {
      if (fPath.indexOf(pattern) !== -1) {
        ignore = true
        break
      }
    }
    if (ignore) continue
    if (!fs.statSync(fPath).isFile()) continue

    const relPath = path.relative('src/', fPath).replace(/\\/g, '/')
    console.log(' Adding to archive: ' + relPath)

    const data = fs.readFileSync(fPath)
    zip.file(relPath, data)
  }

  const data = zip.generate({ base64: false, compression: 'DEFLATE' })
  fs.writeFileSync(destination, data, 'binary')
}
