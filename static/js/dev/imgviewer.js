let $ = window.$

class ImgViewer {
  constructor () {
    this.id = '#odresult'
  }
  getImg (img) {
    $(`${this.container} .content`).attr('src', `data:${img.type};base64,${img.data}`)
  }
  show (visible = true) {
    if (visible === true) {
      $(this.container).show()
    } else {
      $(this.container).hide()
    }
  }
}

export default ImgViewer
