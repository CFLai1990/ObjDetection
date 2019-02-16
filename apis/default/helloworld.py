"""helloworld: default testing api"""
from .__settings__ import API

class ApiClass(API):
    """API Class"""
    def __init__(self, parameters):
        API.__init__(self, parameters)

    def execute(self, data):
        self.emit2client('Hello ' + data + '!')
        self.logger.info('API executed')
