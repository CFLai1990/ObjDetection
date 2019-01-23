let API = require('./API')

class Hello extends API._class {
  constructor (socket, message) {
    super(socket, message)
  }
  exec (usrname) {
    this.socket.emit(this.message, `Hello, ${usrname}!`)
  }
}

module.exports = API._creator(Hello)
