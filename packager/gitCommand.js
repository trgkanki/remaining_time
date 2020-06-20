const { getStdout } = require('./execCommand')
const natCompare = require('natural-compare-lite')

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

exports.getLatestReleaseVersion = async function () {
  const tags = (await getStdout('git tag')).split('\n')
  let lastTag = ''
  for (const tag of tags) {
    // v20.5.9i105
    if (/^v(\d+)\.(\d+)\.(\d+)i(\d+)$/.test(tag)) {
      if (natCompare(lastTag, tag) < 0) lastTag = tag
    }
  }
  return lastTag || undefined
}

exports.getCommitsSinceTag = async function (tag) {
  if (tag) return getStdout(`git log --pretty=oneline ${tag}...HEAD`)
  else return getStdout('git log --pretty=oneline')
}
