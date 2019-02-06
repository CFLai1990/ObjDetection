let FileReader = window.FileReader

class FRead {
  constructor (file) {
    this.file = file
    this.fread = new FileReader()
  }
  getFile (file) {
    this.file = file
  }
  readSuccess () {
    console.info(`Read '${this.file.name}' successfully!`)
  }
  readFailure () {
    console.error(`Failed to read '${this.file.name}'!`)
  }
  read (callback, errorCallback) {
    let cb = callback
    let ecb = errorCallback
    if (cb === undefined || cb === null) {
      cb = (data) => { console.log(data) }
    }
    if (ecb === undefined || ecb === null) {
      ecb = () => {}
    }
    this.fread.readAsDataURL(this.file)
    this.fread.onload = () => {
      this.readSuccess()
      let data = {
        name: this.file.name,
        type: this.file.type,
        size: this.file.size,
        data: this.fread.result
      }
      cb(data)
    }
    this.fread.onerror = () => {
      this.readFailure()
      ecb()
    }
    this.fread.onabort = () => {
      this.readFailure()
      ecb()
    }
  }
}

export default FRead
