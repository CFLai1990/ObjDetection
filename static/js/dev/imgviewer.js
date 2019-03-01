let $ = window.$
/* message:
  'OD_Image': get the image with masks
  'OD_Mask': get the mask parameters
*/

class ImgViewer {
  constructor (message) {
    this.id = '#odresult'
    this.message = message
  }
  getOriginal (img) {
    switch (this.message) {
      case 'OD_Image':
        $(`${this.id} .img`).attr('src', `data:${img.type};base64,${img.data}`)
        break
      case 'OD_Mask':
        console.info('Before:', img)
        break
      case 'OD_Demo':
        console.info('Before:', img)
        break
    }
  }
  getResult (img) {
    switch (this.message) {
      case 'OD_Image':
        $(`${this.id} .img`).attr('src', `data:${img.type};base64,${img.data}`)
        break
      case 'OD_Mask':
        console.info('After:', img)
        break
      case 'OD_Demo':
        console.info('After:', img)
        break
    }
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
