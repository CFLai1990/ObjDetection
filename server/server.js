let express = require('express')
let router = express.Router()
let app = express()
let server = require('http').createServer(app)
let io = require('socket.io')(server)

io.on('connection', function (socket) {
  socket.on('message', function (msg) {
    console.log(msg)
    socket.send('Fine, and you?')
  })
  socket.on('disconnect', function () {})
})

server.listen(5000)

module.exports = router
