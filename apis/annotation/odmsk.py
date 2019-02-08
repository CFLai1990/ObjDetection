from flask_socketio import emit
from .__settings__ import API, fileDir, fileType
import base64
import os
import json

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
    print(type(result))
    result = json.dumps(result)
    self.logger.info('Image detection finished')
    return result

  def execute(self, obj):
    # save the text into file
    result = self.OD(obj)
    self.socket.emit(self.message, result, namespace=self.namespace)
    self.logger.info('Result sent')