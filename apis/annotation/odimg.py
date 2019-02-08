from flask_socketio import emit
from .__settings__ import API, fileDir, fileType
import base64
import os

class apiClass(API):
  def __init__(self, logger, socket, message, namespace, detector):
    API.__init__(self, logger, socket, message, namespace)
    self.typeDict = fileType
    self.outputDir = fileDir
    self.objDetector = detector

  def saveImage(self, obj):
    imgPath = fileDir + '/' + obj['name']
    with open(imgPath, 'wb') as file:
      file.write(base64.b64decode(obj['data']))
      file.close()
    return imgPath

  def loadImage(self, path):
    with open(path, 'rb') as file:
      imgBase64 = str(base64.b64encode(file.read()), 'utf-8') # for Python 3
      file.close()
    return imgBase64

  def OD(self, obj):
    imgPath = self.saveImage(obj)
    self.logger.info('Image saved')
    extType = obj['type']
    imgType = self.typeDict[extType]
    outputPath = self.objDetector.inferImage(imgPath, imgType, self.outputDir)
    self.logger.info('Image detection finished')
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
    self.logger.info('Result sent')