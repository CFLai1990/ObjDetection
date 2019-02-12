from .__settings__ import API

class apiClass(API):
  def __init__(self, parameters):
    API.__init__(self, parameters)

  def execute(self, usrname):
    self.emit2Client('Hello ' + usrname + '!')
    self.logger.info('API executed')