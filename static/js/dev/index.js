import io from 'socket.io-client'
let $ = window.$
let VERSION = 'local'

let callbackCreator = function (socket) {
  let callback = function () {
    socket.on('Test', function (msg) {
      console.log(msg)
    })
    $('#nlptest-submit').on('click', function () {
      let text = $('#nlptest-input').val()
      if (text !== '' || undefined) {
        socket.emit('Test', text)
      }
    })
  }
  return callback
}

$(document).ready(function () {
    // Socket.io demo
  $('#odtest-input').fileinput()
  let socket
  switch (VERSION) {
    case 'local':
      socket = io('http://localhost:2020/api/annotation')
      break
    case 'db':
      socket = io('http://192.168.10.9:2020/api/annotation')
      break
    case 'websocket':
      break
  }
  socket.on('connect', callbackCreator(socket))
})
