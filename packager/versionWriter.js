const shelljs = require('shelljs')
const fs = require('fs')
const { getRepoName } = require('./gitCommand')

exports.updateFilesVersionString = async function (newVersion, changelogMessage) {
  const repoName = await getRepoName()
  console.log(`Updating to "${repoName} v${newVersion}"`)

  shelljs.sed('-i', /"version": "(.+?)"/, `"version": "${newVersion}"`, 'package.json')
  shelljs.sed('-i', /^ {2}"version": "(.+?)"/, `  "version": "${newVersion}"`, 'package-lock.json')
  shelljs.sed('-i', /^# .+v(\d+)\.(\d+)\.(\d+)\.(\d+)$/m, `# ${repoName} v${newVersion}`, 'src/__init__.py')
  fs.writeFileSync('src/VERSION', newVersion)
}
