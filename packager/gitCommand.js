const { getStdout } = require('./execCommand')

exports.checkCleanRepo = async function () {
  const gitStatus = await getStdout('git status')
  if (gitStatus.indexOf('nothing to commit, working tree clean') === -1) {
    throw new Error('Repo not clean. Only can distribute on clean repo')
  }
}

exports.getRepoName = async function () {
  const originUrl = await getStdout('git remote get-url origin')
  const matches = originUrl.match(/.*\/(\w+)\.git/)
  const repoName = matches[1]
  if (!repoName) throw new Error('bad repo name')
  return repoName
}
