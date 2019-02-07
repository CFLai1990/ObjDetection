let $ = window.$

class FileUploader {
  constructor () {
    this.container = '#odtest'
    this.id = '#odtest-input'
    this.uploadOptions = {
      uploadUrl: '/upload',
      allowedFileExtensions: ['jpg', 'png'],
      autoOrientImage: true,
      maxFileCount: 1,
      dropZoneEnable: true,
      maxImageWidth: 200,
      maxImageHeight: 150,
      resizePreference: 'height',
      resizeImage: true
    }
  }
  init () {
    $(this.id).fileinput(this.uploadOptions)
  }
  bind (event, callback) {
    if (event === 'upload') {
      $(`${this.container} .fileinput-upload-button`).on('click', callback)
    } else {
      $(this.id).on(event, callback)
    }
  }
  show (visible = true) {
    if (visible === true) {
      $(this.container).show()
    } else {
      $(this.container).hide()
    }
  }
}

export default FileUploader
