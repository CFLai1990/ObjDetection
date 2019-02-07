from flask_socketio import emit
from .__settings__ import API, fileDir, fileType
from .libs import ObjDetection
import base64
import os

class apiClass(API):
  def __init__(self, logger, socket, message, namespace):
    API.__init__(self, logger, socket, message, namespace)
    self.typeDict = fileType
    self.outputDir = fileDir
    self.objDetector = ObjDetection()

  def saveImage(self, obj):
    imgPath = fileDir + '/' + obj['name']
    imgBase64 = obj['data'].replace('data:' + obj['type'] + ';base64,', '')
    file = open(imgPath, 'wb')
    file.write(base64.b64decode(imgBase64))
    file.close()
    return imgPath

  def loadImage(self, path):
    file = open(path, 'rb')
    imgBinary = file.read()
    imgBase64 = 'data:image/png;base64,' + base64.b64encode(imgBinary)
    file.close()
    return imgBase64

  def OD(self, obj):
    extType = obj['type']
    imgPath = self.saveImage(obj)
    self.logger.info('image saved')
    imgType = self.typeDict[extType]
    outputPath = self.objDetector.infer(imgPath, imgType, self.outputDir)
    self.logger.info('image detection finished')
    outputName = os.path.basename(outputPath)
    imgData = self.loadImage(outputPath)
    result = {
      'name': outputName,
      'type': extType,
      'data': imgData,
    }
    return result

  def execute(self, obj):
    # save the text into file
    result = self.OD(obj)
    self.socket.emit(self.message, result, namespace=self.namespace)
    self.logger.info('result sent')