const NodeZip = require('node-zip')
const walk = require('walkdir')
const fs = require('fs')
const path = require('path')

const ignoreList = [
  '__pycache__',
  'meta.json'
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
