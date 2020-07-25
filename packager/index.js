const utcVersion = require('utc-version')
const { checkCleanRepo, getRepoName } = require('./gitCommand')
const { zipDist } = require('./zipDist')
const { getStdout } = require('./execCommand')
const { updateFilesVersionString } = require('./versionWriter')
const { updateChangelog, inputChangelog } = require('./changelog')
const gitBranchIs = require('git-branch-is')

const fs = require('fs')
const tmp = require('tmp')

;(async function () {
  if (!await gitBranchIs('develop')) {
    throw new Error('You can issue a release only from the develop branch')
  }

  await checkCleanRepo()

  const repoName = await getRepoName()
  const version = utcVersion({ apple: true })

  const changelogMessage = await inputChangelog()
  if (!changelogMessage) {
    throw Error('Empty changelog message')
  }
  console.log(changelogMessage)
  await updateChangelog(version, changelogMessage)

  // Update __init__.py + VERSION
  await updateFilesVersionString(version)

  // Dist zip
  fs.mkdirSync('dist', { recursive: true })
  await zipDist(`dist/${repoName}_v${version}.ankiaddon`)
  await zipDist(`dist_${repoName}.ankiaddon`)

  // Commit
  await getStdout('git add -A')
  const commitMessageFname = tmp.tmpNameSync()
  fs.writeFileSync(commitMessageFname, `:bookmark: v${version}\n\n${changelogMessage}`)
  try {
    await getStdout(`git commit -F "${commitMessageFname}"`)
  } finally {
    fs.unlinkSync(commitMessageFname)
  }

  // Add tag
  await getStdout(`git tag v${version}`)
  await getStdout('git push --tags')

  // Merge to master
  await getStdout('git checkout master')
  await getStdout('git merge develop')
  await getStdout('git checkout develop')

  console.log('Dist + commit done!')
})().catch(err => {
  console.error(err)
  process.exit(-1)
})

// bestzip({
//   source: 'src/*',
//   cwd: 'src/',
//   destination: `./dist${version}.zip`
// }).then(function () {
//   console.log('all done!')
// }).catch(function (err) {
//   console.error(err.stack)
//   process.exit(1)
// })
