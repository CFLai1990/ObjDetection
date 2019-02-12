from flask_socketio import emit
from .__settings__ import API
import base64

class apiClass(API):
  def __init__(self, parameters):
    print('0')
    API.__init__(self, parameters)
    print('1')
    self.objDetector = parameters['detector']
    print('2')

  def saveImage(self, obj):
    imgPath = self.fileOp.getPath(obj['name'])
    with open(imgPath, 'wb') as file:
      file.write(base64.b64decode(obj['data']))
      file.close()
    return imgPath

  def loadImage(self, path):
    with open(path, 'rb') as file:
      imgBase64 = str(base64.b64encode(file.read()), 'utf-8') # for Python 3
      file.close()
    return imgBase64

  def OD_Image(self, obj):
    # Save the original image
    imgPath = self.saveImage(obj)
    self.logger.info('Image saved')
    # Object detection
    extType = obj['type']
    imgType = self.fileOp.getType(extType)
    outputDir = self.fileOp.getRoot()
    outputPath = self.objDetector.inferImage(imgPath, imgType, outputDir)
    self.logger.info('Image detection finished')
    # Load the processed image
    outputName = self.fileOp.getName(outputPath)
    imgData = self.loadImage(outputPath)
    result = {
      'name': outputName,
      'type': extType,
      'data': imgData,
    }
    return result

  def execute(self, obj):
    result = self.OD_Image(obj)
    self.emit2Client(result)
    self.logger.info('Result sent')