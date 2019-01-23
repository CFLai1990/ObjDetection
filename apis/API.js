/*
  Any new api needs to:
  - extend this API class
  - rewrite the exec function
  - rewrite the bindEvent function (if necessary)
*/

class API {
  constructor (socket, message) {
    this.socket = socket
    this.message = message
  }
  bindEvent () {
    // run api.exec when the message is received
    this.socket.on(this.message, (data) => { this.exec(data) })
  }
  exec (data) {
    this.socket.emit(this.message, 'API not found!')
  }
}

function classCreator (APIClass) {
  return function (socket, message, ...pars) {
    return new APIClass(socket, message, ...pars)
  }
}

module.exports = { _class: API, _creator: classCreator }
