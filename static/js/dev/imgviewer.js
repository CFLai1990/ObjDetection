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
      case 'OD_Test':
        console.info('Before:', img)
        break
    }
  }
  getResult (data) {
    switch (this.message) {
      case 'OD_Image':
        $(`${this.id} .img`).attr('src', `data:${data.type};base64,${data.data}`)
        break
      case 'OD_Mask':
        console.info('After:', data)
        break
      case 'OD_Demo':
        console.info('After:', data)
        break
      case 'OD_Test':
        let img = data.image
        $(`${this.id} .img`).attr('src', `data:${img.type};base64,${img.data}`)
        let parameters = data.data
        console.info('After:', parameters)
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
