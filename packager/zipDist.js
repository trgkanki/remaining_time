const NodeZip = require('node-zip')
const walk = require('walkdir')
const fs = require('fs')
const path = require('path')

exports.zipDist = function (destination) {
  const zip = new NodeZip()
  const paths = walk.sync('src')
  for (const fPath of paths) {
    if (fPath.indexOf('__pycache__') !== -1) continue
    if (!fs.lstatSync(fPath).isFile()) continue

    const relPath = path.relative('src/', fPath).replace(/\\/g, '/')
    const data = fs.readFileSync(fPath)
    zip.file(relPath, data)
    console.log(' Adding to archive: ' + relPath)
  }

  const data = zip.generate({ base64: false, compression: 'DEFLATE' })
  fs.writeFileSync(destination, data, 'binary')
}
