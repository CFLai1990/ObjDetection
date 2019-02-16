"""The default APIs class"""
import importlib
from flask import request
from .logger import Logger
from .file import FileOperations as FileOp
from .api import get_client_msg

class APIs:
    """The wrapper for all annotation APIs"""
    def __init__(self, parameters):
        self.namespace = parameters['namespace']
        self.logger = Logger('\'' + self.namespace + '\'', parameters['logger'])
        self.socket = parameters['socket']
        self.package = parameters['package']
        self.api_parameters = {
            'logger': self.logger,
            'socket': self.socket,
            'namespace': self.namespace,
            }
        self.events = parameters['events']
        self.output_dir = parameters['output_dir']
        self.file_ops = {}
        self.clients = {}

    def start(self):
        """Bind the connections"""
        self.connect_socket()
        self.disconnect_socket()

    def api_parms(self, new_dict):
        """Add new parameters to the API"""
        self.api_parameters.update(new_dict)

    def temp_parms(self, new_dict):
        """Temporary parameters for the API"""
        return dict(self.api_parameters, **new_dict)

    def connect_socket(self):
        """Connect events"""
        @self.socket.on('connect', namespace=self.namespace)
        def _callback():
            client_id = request.sid
            self.wait4ready(client_id)

    def wait4ready(self, client_id):
        """Initialize after the connection is stable and ready"""
        @self.socket.on(get_client_msg('__ready__', client_id), namespace=self.namespace)
        def _callback(data):
            self.init_output(client_id)
            self.bind_events(client_id)
            # save the information of the client socket
            self.clients[client_id] = {
                'IP': request.remote_addr,
                'info': data
            }
            self.logger.info('Client connected: ID_' + client_id)

    def init_output(self, client_id):
        """Build the output directory"""
        file_op = FileOp(self.output_dir)
        new_root = file_op.mkdir(client_id)
        file_op.change_root(new_root)
        self.file_ops[client_id] = file_op

    def bind_events(self, client_id):
        """Bind the message for each API"""
        for message, api_name in self.events.items():
            temp_parameters = self.temp_parms({
                'message': message,
                'client_id': client_id,
                'file_op': self.file_ops[client_id]
            })
            importlib.import_module('.' + api_name, package=self.package).ApiClass(temp_parameters)

    def unbind_events(self, client_id):
        """Unbind the message for each API"""
        for message in self.events:
            @self.socket.on(get_client_msg(message, client_id), namespace=self.namespace)
            def _callback():
                pass

    def rm_output(self, client_id):
        """Remove the output directory"""
        file_op = self.file_ops[client_id]
        file_op.change_root(self.output_dir)
        file_op.rmdir(client_id)
        del self.file_ops[client_id]

    def disconnect_socket(self):
        """Disconnect events"""
        @self.socket.on('disconnect', namespace=self.namespace)
        def _callback():
            client_id = request.sid
            if self.clients.get(client_id) is not None:
                del self.clients[client_id]
                self.unbind_events(client_id)
                self.rm_output(client_id)
                self.logger.info('Client disconnected: ID_' + client_id)
                