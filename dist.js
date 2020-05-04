const bestzip = require('bestzip')
const exec = require('child_process').exec
const utcVersion = require('utc-version')
const shelljs = require('shelljs')
const fs = require('fs')

function getStdout (command) {
  return new Promise((resolve, reject) => {
    exec(command, (err, stdout) => {
      if (err) return reject(err)
      return resolve(stdout)
    })
  })
}

async function checkCleanRepo () {
  const gitStatus = await getStdout('git status')
  if (gitStatus.indexOf('nothing to commit, working tree clean') === -1) {
    throw new Error('Repo not clean. Only can distribute on clean repo')
  }
}

async function getRepoName () {
  const originUrl = await getStdout('git remote get-url origin')
  const matches = originUrl.match(/.*\/(\w+)\.git/)
  const repoName = matches[1]
  if (!repoName) throw new Error('bad repo name')
  return repoName
}

function zipDist (destination) {
  return bestzip({
    source: '*',
    cwd: 'src/',
    destination
  })
}

(async function () {
  await checkCleanRepo()

  const repoName = await getRepoName()
  const version = utcVersion({ apple: true })

  // Update __init__.py + VERSION
  console.log(`Updating to "${repoName} v${version}"`)
  shelljs.sed('-i', /"version": "(.+?)"/, `"version": "${version}"`, 'package.json')
  shelljs.sed('-i', /^# .+v(\d+)\.(\d+)\.(\d+)\.(\d+)$/m, `# ${repoName} v${version}`, 'src/__init__.py')
  fs.writeFileSync('src/VERSION', version)

  // Dist zip
  fs.mkdirSync('dist', { recursive: true })
  await zipDist(`../dist/${repoName}_v${version}.zip`)
  await zipDist('../dist.zip')

  // Add tag
  await getStdout('git add -A')
  await getStdout(`git commit -m ":bookmark: v${version}`)
  await getStdout(`git tag v${version}`)

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
