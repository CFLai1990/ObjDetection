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

  def OD(self, obj):
    imgPath = self.saveImage(obj)
    self.logger.info('Image saved')
    result = self.objDetector.inferParameters(imgPath)
    self.logger.info('Image detection finished')
    return result

  def execute(self, obj):
    # save the text into file
    result = self.OD(obj)
    test=['1','2','3']
    self.socket.emit(self.message, test, namespace=self.namespace)
    self.logger.info('Result sent')