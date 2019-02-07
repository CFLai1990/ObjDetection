let $ = window.$

class ImgViewer {
  constructor () {
    this.id = '#odresult'
  }
  getImg (img) {
    $(`${this.id} .content`).attr('src', `data:${img.type};base64,${img.data}`)
  }
  show (visible = true) {
    if (visible === true) {
      $(this.id).show()
    } else {
      $(this.id).hide()
    }
  }
}

export default ImgViewer
