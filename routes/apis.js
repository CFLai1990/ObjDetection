let express = require('express')
let router = express.Router()
let Hello = require('../apis/Hello')

/* GET API services. */
router.get('/', function (req, res, next) {
  res.io.on('Hello', Hello.exec(req))
  res.send('respond with a resource.')
})

module.exports = router
