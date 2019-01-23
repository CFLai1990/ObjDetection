const { createLogger, format, transports } = require('winston')
const { combine, timestamp, label, printf } = format

const myFormat = printf(info => {
  return `${info.timestamp} [${info.label}] ${info.level}: ${info.message}`
})

function myLogger (myLabel) {
  const logger = createLogger({
    format: combine(
            label({ label: `${myLabel}` }),
            timestamp({format: 'YYYY-MM-DD HH:mm:ss'}),
            myFormat
        ),
    transports: [new transports.Console()]
  })
  return logger
}

module.exports = myLogger
