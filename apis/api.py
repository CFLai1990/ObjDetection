from flask_socketio import emit

class API:
  'The universal API class'
  def __init__(self, socket, message):
    self.socket = socket
    self.message = message
    self.bindEvents()

  def bindEvents(self):
    @self.socket.on(self.message, namespace='/apis')
    def call_back(data):
      self.exec(data)

  def exec(self, data):
    self.socket.emit(self.message, 'API not found!')
