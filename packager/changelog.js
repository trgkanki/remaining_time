const tmp = require('tmp')
const fs = require('fs')
const format = require('date-fns/format')

const { getLatestReleaseVersion, getCommitsSinceTag, getRepoName } = require('./gitCommand')
const { renderMarkdownHTML } = require('./markedHTMLRenderer')
const { getStdout } = require('./execCommand')

exports.inputChangelog = async function () {
  const lastVersion = await getLatestReleaseVersion()
  const commitLogs = await getCommitsSinceTag(lastVersion)

  const mdTemplate = `\n\n<!---\nWrite your changelog in markdown format above. Anything in this comment region is ignored.\n\n${commitLogs}\n-->\n`
  const tmpName = tmp.tmpNameSync({ postfix: '.md' })

  fs.writeFileSync(tmpName, mdTemplate, { encoding: 'utf-8' })
  try {
    await getStdout(`code --wait "${tmpName}"`)
    return (
      fs.readFileSync(tmpName, { encoding: 'utf-8' })
        .replace(/<!---(.|\n)*?-->/g, '')
        .trim()
    )
  } finally {
    fs.unlinkSync(tmpName)
  }
}

exports.updateChangelog = async function (version, changelogMd) {
  const dateString = format(new Date(), 'yyyy-MM-dd')
  const changelogMarkerComment = '[comment]: # (DO NOT MODIFY. new changelog goes here)'
  const changelogSectionMd = `${changelogMarkerComment}\n\n## ${version} (${dateString})\n\n` + changelogMd

  const changelogPath = 'CHANGELOG.md'
  if (fs.existsSync(changelogPath)) {
    let md = fs.readFileSync(changelogPath, { encoding: 'utf-8' })
    md = md.replace(changelogMarkerComment, changelogSectionMd)
    fs.writeFileSync(changelogPath, md, { encoding: 'utf-8' })
  } else {
    const repoName = await getRepoName()
    const initialFileContent = `# Changelog of ${repoName}\n\n${changelogSectionMd}\n`
    fs.writeFileSync(changelogPath, initialFileContent, { encoding: 'utf-8' })
  }

  compileChangelogMarkdown(await getRepoName())
}

function compileChangelogMarkdown (repoName) {
  const changelogPath = 'CHANGELOG.md'
  const outputPath = 'src/CHANGELOG.html'

  fs.writeFileSync(outputPath,
    renderMarkdownHTML(repoName, fs.readFileSync(changelogPath, { encoding: 'utf-8' })),
    { encoding: 'utf-8' }
  )
}
