import FRead from './filereader.js'
import FLoad from './fileuploader.js'
import IView from './imgviewer.js'
import Modal from './loading.js'

class FSocket {
  constructor (socket, message) {
    this.socket = socket
    this.message = message
    this.data = null
    this.fread = new FRead()
    this.fload = new FLoad()
    this.iview = new IView(message)
    this.mdl = new Modal()
    this.fload.init()
  }
  getData (data) {
    this.data = data
  }
  handleEmit () {
    this.socket.emit(this.message, this.data)
    console.info(`File '${this.data.name}' uploaded!`)
  }
  handleUpload () {
    // Read the file when uploaded
    this.fload.bind('fileloaded', (event, file) => {
      this.fread.getFile(file)
      this.fread.read((data) => {
        this.getData(data)
      })
    })
    // Remove the file when cleared
    this.fload.bind('fileclear', () => {
      console.log(`File '${this.data.name}' removed!`)
      this.fread.getFile(null)
    })
    // Upload the file
    this.fload.bind('upload', () => {
      if (this.data !== null) {
        // Show the original image
        this.fload.show(false)
        this.iview.getOriginal(this.data)
        this.iview.show()
        // Upload the original image
        this.handleEmit()
        this.mdl.show(true, 'Running object detection ...')
      }
    })
  }
  handleReceive () {
    this.socket.on(this.message, (data) => {
      // Show the processed image
      this.iview.getResult(data)
      this.iview.show()
      this.mdl.show(false)
    })
  }
  onConnect () {
    this.handleUpload()
    this.handleReceive()
  }
}

export default FSocket
