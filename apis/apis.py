from .libs import Logger

# the default APIs
from .default import APIs as defaultAPIs
from .default import namespace as defaultNamespace

# the router dictionary
# namespace: APIsClass
routerDict = {
  defaultNamespace: defaultAPIs,
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

    def routeByNamespace(self):
      for namespace, APIsClass in routerDict.items():
        apisDict[namespace] = APIsClass(self.logger, self.socket)
