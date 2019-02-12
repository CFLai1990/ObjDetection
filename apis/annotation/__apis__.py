# Socket.io handlers
import importlib
from .__settings__ import Logger, namespace, packageName, FileOp, outputDir
from flask import request
from .libs import ObjDetection

# message - apiName
eventDict = {
  'OD_Image': 'odimg',
  'OD_Mask': 'odmsk'
}

class APIs:
    'The wrapper for all annotation APIs'
    def __init__(self, logger, socket):
      self.logger = Logger('\'' + namespace + '\'', logger)
      self.socket=socket
      self.connectSocket()
      self.disconnectSocket()
      self.outputDir = outputDir
      self.fileOps = {}
      self.objDetector = ObjDetection()

    def connectSocket(self):
      @self.socket.on('connect', namespace=namespace)
      def test_connect():
        clientID = request.sid
        self.initOutput(clientID)
        self.bindEvents(clientID)
        self.logger.info('Client connected: [ID]' + clientID)
        return clientID

    def initOutput(self, clientID):
      fOp = FileOp(self.outputDir)
      newRoot = fOp.mkdir(clientID)
      fOp.changeRoot(newRoot)
      self.fileOps[clientID] = fOp

    def bindEvents(self, clientID):
      for message,apiName in eventDict.items():
        print(message)
        api = importlib.import_module('.' + apiName, package=packageName).apiClass({
          'logger': self.logger,
          'socket': self.socket, 
          'message': message, 
          'namespace': namespace,
          'clientID': clientID,
          'fileOp': self.fileOps[clientID],
          'detector': self.objDetector
          })

    def unbindEvents(self, clientID):
      for message,apiName in eventDict.items():
        messageByRoom = message + '_' + clientID
        @self.socket.on(messageByRoom, namespace=namespace)
        def call_back():
          pass

    def rmOutput(self, clientID):
      fOp = self.fileOps[clientID]
      fOp.changeRoot(self.outputDir)
      fOp.rmdir(clientID)
      del self.fileOps[clientID]

    def disconnectSocket(self):
      @self.socket.on('disconnect', namespace=namespace)
      def test_disconnect():
        clientID = request.sid
        self.unbindEvents(clientID)
        self.rmOutput(clientID)
        self.logger.info('Client disconnected: [ID]' + clientID)
