const utcVersion = require('utc-version')
const { checkCleanRepo, getRepoName } = require('./gitCommand')
const { zipDist } = require('./zipDist')
const { getStdout } = require('./execCommand')
const { updateFilesVersionString } = require('./versionUpdater')
const fs = require('fs')

;(async function () {
  await checkCleanRepo()

  const repoName = await getRepoName()
  const version = utcVersion({ apple: true })

  // Update __init__.py + VERSION
  await updateFilesVersionString(version)

  // Dist zip
  fs.mkdirSync('dist', { recursive: true })
  await zipDist(`dist/${repoName}_v${version}.zip`)
  await zipDist('dist.zip')

  // Add tag
  await getStdout('git add -A')
  await getStdout(`git commit -m ":bookmark: v${version}"`)
  await getStdout(`git tag v${version}`)
  await getStdout('git push --tags')

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
