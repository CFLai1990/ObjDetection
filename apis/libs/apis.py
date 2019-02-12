import importlib
from .logger import Logger
from .file import FileOperations as FileOp
from .api import Msg
from flask import request

class APIs:
    'The wrapper for all annotation APIs'
    def __init__(self, parameters):
      self.namespace = parameters['namespace']
      self.logger = Logger('\'' + self.namespace + '\'', parameters['logger'])
      self.socket=parameters['socket']
      self.package = parameters['package']
      self.apiParameters = {
          'logger': self.logger,
          'socket': self.socket, 
          'namespace': self.namespace,
          }
      self.events = parameters['events']
      self.outputDir = parameters['outputDir']
      self.fileOps = {}
      self.clients = {}

    def start(self):
      self.connectSocket()
      self.disconnectSocket()

    def apiParms(self, newDict):
      self.apiParameters.update(newDict)

    def tempParms(self, newDict):
      return dict(self.apiParameters, **newDict)

    def connectSocket(self):
      @self.socket.on('connect', namespace=self.namespace)
      def test_connect():
        clientID = request.sid
        self.wait4Ready(clientID)

    def wait4Ready(self, clientID):
      @self.socket.on(Msg('__ready__', clientID), namespace=self.namespace)
      def init_socket(clientInfo):
        self.initOutput(clientID)
        self.bindEvents(clientID)
        # save the information of the client socket
        self.clients[clientID] = {
          'IP': request.remote_addr,
          'info': clientInfo
        }
        self.logger.info('Client connected: ID_' + clientID)

    def initOutput(self, clientID):
      fOp = FileOp(self.outputDir)
      newRoot = fOp.mkdir(clientID)
      fOp.changeRoot(newRoot)
      self.fileOps[clientID] = fOp

    def bindEvents(self, clientID):
      for message,apiName in self.events.items():
        tempParameters = self.tempParms({
        'message': message, 
        'clientID': clientID,
        'fileOp': self.fileOps[clientID]
        })
        api = importlib.import_module('.' + apiName, package=self.package).apiClass(tempParameters)

    def unbindEvents(self, clientID):
      for message,apiName in self.events.items():
        @self.socket.on(Msg(message, clientID), namespace=self.namespace)
        def call_back():
          pass

    def rmOutput(self, clientID):
      fOp = self.fileOps[clientID]
      fOp.changeRoot(self.outputDir)
      fOp.rmdir(clientID)
      del self.fileOps[clientID]

    def disconnectSocket(self):
      @self.socket.on('disconnect', namespace=self.namespace)
      def test_disconnect():
        clientID = request.sid
        if not(self.clients.get(clientID) is None):
          del self.clients[clientID]
          self.unbindEvents(clientID)
          self.rmOutput(clientID)
          self.logger.info('Client disconnected: ID_' + clientID)