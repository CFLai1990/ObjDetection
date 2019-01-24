# Socket.io handlers
import importlib
from .__settings__ import namespace, packageName

# message - apiName
eventDict = {
  'Hello': 'helloworld',
}

class APIs:
    'The wrapper for all default APIs'
    def __init__(self, socket):
      self.socket=socket
      self.connectSocket()
      self.bindEvents()
      self.disconnectSocket()

    def connectSocket(self):
      @self.socket.on('connect', namespace=namespace)
      def test_connect():
        print('Client connected, namespace: ' + namespace)

    def bindEvents(self):
      for message,apiName in eventDict.items():
        api = importlib.import_module('.' + apiName, package=packageName).apiClass(self.socket, message, namespace)

    def disconnectSocket(self):
      @self.socket.on('disconnect', namespace=namespace)
      def test_disconnect():
        print('Client disconnected, namespace: ' + namespace)
