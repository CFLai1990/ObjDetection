from flask_socketio import emit
from .api import API

class apiClass(API):
  def __init__(self, socket, message):
    API.__init__(self, socket, message)

  def exec(self, usrname):
    self.socket.emit(self.message, 'Hello ' + usrname + '!', namespace='/apis')