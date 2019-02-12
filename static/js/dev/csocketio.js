import io from 'socket.io-client'

const globalAddress = {
  'local': 'localhost',
  'db': '192.168.10.9',
  'dl': '192.168.10.21'
}

const IOSettings = {
  'force new connection': false
}

const Msg = (message, clientID) => { return message + '@' + clientID }

class ClientSocket {
  constructor (parms) {
    this.socket = parms['socket']
    this.namespace = parms['namespace']
  }
  emit (message, data) {
    this.socket.emit(Msg(message, this.id), data)
  }
  on (message, callback) {
    switch (message) {
      case 'connect':
        this.socket.on('connect', () => {
          this.id = this.socket.id.replace(`/${this.namespace}#`, '')
          this.emit('__ready__', this.getInfo())
          this.autoClose()
          callback()
        })
        break
      case 'disconnect':
        this.socket.on('disconnect', callback)
        break
      default:
        this.socket.on(Msg(message, this.id), callback)
        break
    }
  }
  getInfo () {
        // Return the information of this client for registration on server
    return this.id
  }
  autoClose () {
    window.onbeforeunload = function (e) {
      this.socket.close()
    }
  }
}

class ClientIO {
  constructor ({ address, port, namespace, setting = {} }) {
    let realAddress = address
    if (globalAddress[address] !== undefined) {
      realAddress = globalAddress[address]
    }
    this.url = `http://${realAddress}:${port}/${namespace}`
    this.setting = Object.assign(setting, IOSettings)
    return new ClientSocket({
      socket: io(this.url, this.setting),
      namespace: namespace
    })
  }
}

export default ClientIO
