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

const shelljs = require('shelljs')
const fs = require('fs')
const { getRepoName } = require('./gitCommand')

exports.updateFilesVersionString = async function (newVersion, changelogMessage) {
  const repoName = await getRepoName()
  console.log(`Updating to "${repoName} v${newVersion}"`)

  shelljs.sed('-i', /"version": "(.+?)"/, `"version": "${newVersion}"`, 'package.json')
  shelljs.sed('-i', /^ {2}"version": "(.+?)"/, `  "version": "${newVersion}"`, 'package-lock.json')
  shelljs.sed('-i', /^# .+v(\d+)\.(\d+)\.(\d+)[i.](\d+)$/m, `# ${repoName} v${newVersion}`, 'src/__init__.py')
  fs.writeFileSync('src/VERSION', newVersion)
}
