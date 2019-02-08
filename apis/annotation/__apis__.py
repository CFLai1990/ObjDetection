# Socket.io handlers
import importlib
from .__settings__ import Logger, namespace, packageName
from .libs import ObjDetection

# message - apiName
eventDict = {
  'OD_Image': 'odimg',
  'OD_Mask': 'odpar'
}

class APIs:
    'The wrapper for all annotation APIs'
    def __init__(self, logger, socket):
      self.logger = Logger('\'' + namespace + '\'', logger)
      self.socket=socket
      self.objDetector = ObjDetection()
      self.connectSocket()
      self.bindEvents()
      self.disconnectSocket()

    def connectSocket(self):
      @self.socket.on('connect', namespace=namespace)
      def test_connect():
        self.logger.info('Client connected')

    def bindEvents(self):
      for message,apiName in eventDict.items():
        api = importlib.import_module('.' + apiName, package=packageName).apiClass(self.logger, self.socket, message, namespace, self.objDetector)

    def disconnectSocket(self):
      @self.socket.on('disconnect', namespace=namespace)
      def test_disconnect():
        self.logger.info('Client disconnected')
