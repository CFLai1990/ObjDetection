let express = require('express')
let path = require('path')
let cookieParser = require('cookie-parser')
let logger = require('morgan')

let indexRouter = require('./routes/index')
let usersRouter = require('./routes/users')

let app = express()
let server = require('http').Server(app)
let io = require('socket.io')(server)
let apisIO = io.of('/apis') // bind to the 'apis' namespace
let apis = require('./apis/index')
apis.bind(apisIO)

app.use(logger('dev'))
app.use(express.json())
app.use(express.urlencoded({ extended: false }))
app.use(cookieParser())
app.use(express.static(path.join(__dirname, 'public')))

app.use('/', indexRouter)
app.use('/users', usersRouter)

module.exports = {app: app, server: server}
