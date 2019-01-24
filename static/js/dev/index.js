import io from 'socket.io-client'
import $ from 'jquery'
window.$ = $

let callbackCreator = function (socket) {
  let callback = function () {
    socket.on('Hello', function (msg) {
      console.log(msg)
    })
    $('#nlptest-submit').on('click', function () {
      let text = $('#nlptest-input').val()
      if (text !== '' || undefined) {
        socket.emit('Hello', text)
      }
    })
  }
  return callback
}

$(document).ready(function () {
    // Socket.io demo
  let socket = io('http://localhost:5000/api')
  socket.on('connect', callbackCreator(socket))
})
