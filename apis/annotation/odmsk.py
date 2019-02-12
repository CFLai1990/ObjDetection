from flask_socketio import emit
from .__settings__ import API
import base64

class apiClass(API):
  def __init__(self, parameters):
    API.__init__(self, parameters)
    self.objDetector = parameters['detector']

  def saveImage(self, obj):
    imgPath = self.fileOp.getPath(obj['name'])
    with open(imgPath, 'wb') as file:
      file.write(base64.b64decode(obj['data']))
      file.close()
    return imgPath

  def OD_Mask(self, obj):
    # Save the original image
    imgPath = self.saveImage(obj)
    self.logger.info('Image saved')
    # Object detection
    result = self.objDetector.inferParameters(imgPath)
    self.logger.info('Image detection finished')
    return result

  def execute(self, obj):
    result = self.OD_Mask(obj)
    self.emit2Client(result)
    self.logger.info('Result sent')