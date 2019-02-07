import FRead from './filereader.js'
import FLoad from './fileuploader.js'
import IView from './imgviewer.js'

class FSocket {
  constructor (socket) {
    this.socket = socket
    this.message = 'Test'
    this.data = null
    this.fread = new FRead()
    this.fload = new FLoad()
    this.iview = new IView()
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
        this.iview.getImg(this.data)
        this.iview.show()
        // Upload the original image
        this.handleEmit()
      }
    })
  }
  handleReceive () {
    this.socket.on(this.message, (data) => {
      // Show the processed image
      this.iview.getImg(data)
      this.iview.show()
    })
  }
  callback () {
    this.handleUpload()
    this.handleReceive()
  }
}

export default FSocket
