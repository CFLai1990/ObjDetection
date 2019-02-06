from flask_socketio import emit
from .logger import Logger

class API:
  'The universal API class'
  def __init__(self, logger, socket, message, namespace):
    self.socket = socket
    self.message = message
    self.namespace = namespace
    self.logger = Logger('\'' + self.message + '\'', logger)
    self.bindEvents()

  def bindEvents(self):
    @self.socket.on(self.message, namespace=self.namespace)
    def call_back(data):
      self.logger.info('Message received')
      self.execute(data)

  def execute(self, data):
    self.socket.emit('API not found!')
