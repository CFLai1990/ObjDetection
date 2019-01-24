# Socket.io handlers
from flask_socketio import emit
import importlib

#message - apiPath
eventDict = {
  'Hello': '.hello',
}

class APIs:
    'The wrapper for all APIs'
    def __init__(self, socket):
      self.socket=socket
      self.connectSocket()
      self.bindEvents()
      self.disconnectSocket()

    def connectSocket(self):
      @self.socket.on('connect', namespace='/apis')
      def test_connect():
        print('Client connected')

    def bindEvents(self):
      for message,apiPath in eventDict.items():
        api = importlib.import_module(apiPath, package='apis').apiClass(self.socket, message)

    def disconnectSocket(self):
      @self.socket.on('disconnect', namespace='/apis')
      def test_disconnect():
        print('Client disconnected')
