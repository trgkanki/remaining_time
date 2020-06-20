const exec = require('child_process').exec

exports.getStdout = function (command) {
  return new Promise((resolve, reject) => {
    exec(command, (err, stdout) => {
      if (err) return reject(err)
      return resolve(stdout)
    })
  })
}
