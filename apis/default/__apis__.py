# Socket.io handlers
from .__settings__ import APIs, namespace, package, outputDir, eventDict

class THIS_APIs(APIs):
    'The wrapper for all default APIs'
    def __init__(self, logger, socket):
      APIs.__init__(self, {
        'namespace': namespace,
        'logger': logger,
        'socket': socket,
        'events': eventDict,
        'package': package,
        'outputDir': outputDir
      })
      self.start()
