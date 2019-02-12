from .libs import Logger

# the default APIs
from .default import APIs as defaultAPIs
from .default import namespace as defaultNamespace

# the default APIs
from .annotation import APIs as antAPIs
from .annotation import namespace as antNamespace

# the router dictionary
# namespace: APIsClass
routerDict = {
  defaultNamespace: defaultAPIs,
  antNamespace: antAPIs,
}

# the APIs dictionary
# namespace: APIsInstance
apisDict = {}

class APIs:
    'The wrapper for all APIs'
    def __init__(self, logger, socket):
      self.socket=socket
      self.logger = Logger('APIs', logger)
      self.routeByNamespace()
      self.logger.info('Server started')

    def routeByNamespace(self):
      for namespace, APIsClass in routerDict.items():
        apisDict[namespace] = APIsClass(self.logger, self.socket)
