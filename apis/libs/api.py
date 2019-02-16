"""The default API class"""
from .logger import Logger

def get_client_msg(message, client_id):
    """get_client_msg: get the client-based-message"""
    return message + '@' + client_id

class API:
    """The universal API class"""
    def __init__(self, parameters):
        self.socket = parameters['socket']
        self.message = parameters['message']
        self.namespace = parameters['namespace']
        self.client_id = parameters['client_id']
        if parameters['file_op'] is not None:
            self.file_op = parameters['file_op']
        self.logger = Logger('\'' + self.message + '\'', parameters['logger'])
        self.bind_events()

    def bind_events(self):
        """bind the message for this api"""
        self.client_msg = get_client_msg(self.message, self.client_id)
        @self.socket.on(self.client_msg, namespace=self.namespace)
        def _callback(data):
            self.logger.info('Message received: ID_' + self.client_id)
            self.execute(data)

    def execute(self, data):
        """the default execute function"""
        self.logger.info('Received from client: ' + data)
        self.emit2client('API not found!')

    def emit2client(self, data, namespace=None, room=None):
        """the emit function"""
        if namespace is None:
            namespace = self.namespace
        if room is None:
            room = self.client_id
        self.socket.emit(self.client_msg, data, namespace=namespace, room=room)
