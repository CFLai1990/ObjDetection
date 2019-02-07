from flask_socketio import emit
from .__settings__ import API, filePath, fileType
from .libs import ObjDetection
import base64
import os

class apiClass(API):
  def __init__(self, logger, socket, message, namespace):
    API.__init__(self, logger, socket, message, namespace)
    self.typeDict = fileType
    self.outputPath = filePath
    self.objDetector = ObjDetection()

  def saveImage(self, obj):
    imgPath = filePath + '/' + obj['name']
    imgBase64 = obj['data'].replace('data:' + obj['type'] + ';base64,', '')
    file = open(imgPath, 'wb')
    file.write(base64.b64decode(imgBase64))
    file.close()
    return imgPath

  def loadImage(self, path, type):
    file = open(path, 'rb')
    imgBinary = file.read()
    imgBase64 = 'data:' + type + ';base64,' + base64.b64encode(imgBinary)
    file.close()
    return imgBase64

  def OD(self, obj):
    extType = obj['type']
    imgPath = self.saveImage(obj)
    imgType = self.typeDict[extType]
    outputPath = self.objDetector.infer(imgPath, imgType, self.outputPath)
    outputName = os.path.basename(outputPath)
    imgData = self.loadImage(outputPath, extType)
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
    self.logger.info('API executed')