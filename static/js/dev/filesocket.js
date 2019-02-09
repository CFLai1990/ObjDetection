import FRead from './filereader.js'
import FLoad from './fileuploader.js'
import IView from './imgviewer.js'
import Modal from './loading.js'

class FSocket {
  constructor (socket) {
    this.socket = socket
    /* message:
      'OD_Image': get the image with masks
      'OD_Mask': get the mask parameters
    */
    this.message = 'OD_Image'
    this.data = null
    this.fread = new FRead()
    this.fload = new FLoad()
    this.iview = new IView()
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
        this.iview.getImg(this.data)
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
      switch (this.message) {
        case 'OD_Image':
          this.iview.getImg(data)
          this.iview.show()
          break
        case 'OD_Mask':
          console.log(data)
          break
      }
      this.mdl.show(false)
    })
  }
  callback () {
    this.handleUpload()
    this.handleReceive()
  }
}

export default FSocket
