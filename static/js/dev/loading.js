let $ = window.$

class Loading {
  show (visible = true, msg) {
    if (visible === true) {
      $('body').loadingModal({ text: msg })
                .loadingModal('animation', 'threeBounce')
                .loadingModal('backgroundColor', 'black')
    } else {
      $('body').loadingModal('hide')
      setTimeout(() => {
        $('body').loadingModal('destroy')
      }, 200)
    }
  }
}

export default Loading
