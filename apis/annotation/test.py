from flask_socketio import emit
from .__settings__ import API, filePath
import base64

class apiClass(API):
  def __init__(self, logger, socket, message, namespace):
    API.__init__(self, logger, socket, message, namespace)
    self.typeDict = {
      'image/jpeg': 'jpg',
      'image/png': 'png',
    }

  def saveImage(self, obj):
    self.imgName = filePath + '/' + obj['name']
    imgBase64 = obj['data'].replace('data:' + obj['type'] + ';base64,', '')
    file = open(self.imgName, 'wb')
    file.write(base64.b64decode(imgBase64))
    file.close()

  def OD(self):
    temp = 1

  def execute(self, obj):
    # save the text into file
    self.saveImage(obj)
    self.OD()
    self.socket.emit(self.message, 'Object Detection executed!', namespace=self.namespace)
    self.logger.info('API executed')