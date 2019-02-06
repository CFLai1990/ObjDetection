from flask_socketio import emit
from .__settings__ import API

class apiClass(API):
  def __init__(self, logger, socket, message, namespace):
    API.__init__(self, logger, socket, message, namespace)

  def OD(self, text):
    temp=text

  def execute(self, text):
    # save the text into file
    self.OD(text)
    self.socket.emit(self.message, 'Object Detection executed!', namespace=self.namespace)
    self.logger.info('API executed')