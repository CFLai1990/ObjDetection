# the default APIs
from .default import APIs as defaultAPIs
from .default import namespace as defaultNamespace

# the router dictionary
# namespace: APIsClass
routerDict = {
  defaultNamespace: defaultAPIs,
}

class APIs:
    'The wrapper for all APIs'
    def __init__(self, socket):
      self.socket=socket
      self.routeByNamespace()

    def routeByNamespace(self):
      for namespace, APIsClass in routerDict.items():
        APIs = APIsClass(self.socket)
