from flask_socketio import emit
from .__settings__ import API

class apiClass(API):
  def __init__(self, logger, socket, message, namespace):
    API.__init__(self, logger, socket, message, namespace)

  def execute(self, usrname):
    self.socket.emit(self.message, 'Hello ' + usrname + '!', namespace=self.namespace)
    self.logger.info('API executed')