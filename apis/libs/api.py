from flask_socketio import emit
from .logger import Logger

def Msg(message, clientID):
  return message + '@' + clientID

class API:
  'The universal API class'
  def __init__(self, parameters):
    self.socket = parameters['socket']
    self.message = parameters['message']
    self.namespace = parameters['namespace']
    self.clientID = parameters['clientID']
    if not(parameters['fileOp'] is None):
      self.fileOp = parameters['fileOp']
    self.logger = Logger('\'' + self.message + '\'', parameters['logger'])
    self.bindEvents()

  def bindEvents(self):
    self.clientMsg = Msg(self.message, self.clientID)
    @self.socket.on(self.clientMsg, namespace=self.namespace)
    def call_back(data):
      self.logger.info('Message received: ID_' + self.clientID)
      self.execute(data)

  def execute(self, data):
    self.emit2Client('API not found!')

  def emit2Client(self, data, namespace=None, room=None):
    if namespace is None:
      namespace = self.namespace
    if room is None:
      room = self.clientID
    self.socket.emit(self.clientMsg, data, namespace=namespace, room=room)
