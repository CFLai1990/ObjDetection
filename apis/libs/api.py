from flask_socketio import emit
from .logger import Logger

class API:
  'The universal API class'
  def __init__(self, parameters):
    print('00')
    self.socket = parameters['socket']
    print('01')
    self.message = parameters['message']
    print('02')
    self.namespace = parameters['namespace']
    print('03')
    self.clientID = parameters['clientID']
    print('04')
    if not(parameters['fileOp'] is None):
      self.fileOp = parameters['fileOp']
    print('05')
    self.logger = Logger('\'' + self.message + '\'', parameters['logger'])
    print('06')
    self.bindEvents()
    print('07')

  def bindEvents(self):
    @self.socket.on(self.message, namespace=self.namespace, room=self.clientID)
    def call_back(data):
      self.logger.info('Message received')
      self.execute(data)

  def execute(self, data):
    self.emit2Client('API not found!')

  def emit2Client(self, data, namespace=None, room=None):
    if namespace is None:
      namespace = self.namespace
    if room is None:
      room = self.clientID
    self.socket.emit(self.message, data, namespace=namespace, room=room)
