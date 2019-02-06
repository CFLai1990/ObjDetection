import io from 'socket.io-client'
import FSocket from './filesocket.js'
let $ = window.$
let VERSION = 'dl'

$(document).ready(function () {
    // Socket.io demo
  let socket
  switch (VERSION) {
    case 'local':
      socket = io('http://localhost:2020/api/annotation')
      break
    case 'db':
      socket = io('http://192.168.10.9:2020/api/annotation')
      break
    case 'dl':
      socket = io('http://192.168.10.21:2020/api/annotation')
      break
    case 'public':
      break
  }
  let fsocket = new FSocket(socket)
  socket.on('connect', () => { fsocket.callback() })
})
