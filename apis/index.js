const logger = require('../logger/logger')('NLP_APIs')

let events = [ // [message, API_path]
    ['Hello', './Hello']
]

class APIs {
  constructor (io) {
    this.io = io
    this.bindSocket()
  }
  bindSocket () {
    this.io.on('connection', (socket) => {
      this.connectSocket(socket)
      this.bindEvents(socket)
      this.disconnectSocket(socket)
    })
  }
  connectSocket (socket) {
    let clientIP = socket.handshake.address
    logger.info(`APIs connected: ${clientIP}`)
  }
  disconnectSocket (socket) {
    let clientIP = socket.handshake.address
    socket.on('disconnect', () => {
      logger.info(`APIs disconnected: ${clientIP}`)
    })
  }
  bindEvents (socket) {
    this.events = new Map() // events: key - event, value: API
    for (let [message, apiPath] of events) {
      let api = require(apiPath)(socket, message)
      api.bindEvent()
      this.events.set(message, api)
    }
  }
}

function APIsConnector (io) {
  return new APIs(io)
}

module.exports = { bind: APIsConnector }
