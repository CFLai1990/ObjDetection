import ClientIO from './csocketio.js'
import FSocket from './filesocket.js'
/* message:
  'OD_Demo': get the artificial data for the demo images
  'OD_Image': get the image with masks
  'OD_Mask': get the mask parameters
  'OD_Test': get the masked image along with the parameters
*/
// const MESSAGE = 'OD_Demo'
// const MESSAGE = 'OD_Image'
const MESSAGE = 'OD_Mask'
// const MESSAGE = 'OD_Test'
const MACHINE = 'dl'
// const VERSION = 'dev'
const VERSION = 'public'
let $ = window.$

$(document).ready(function () {
    // Socket.io demo
  let socket = new ClientIO({
    'address': MACHINE,
    'port': VERSION === 'dev' ? 2021 : 2020,
    'namespace': 'api/annotation'
  })
  let fsocket = new FSocket(socket, MESSAGE)
  socket.on('connect', () => {
      // add more callbacks if necessary
    fsocket.onConnect()
  })
})
