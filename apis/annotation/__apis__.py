# Socket.io handlers
from .__settings__ import APIs, namespace, package, outputDir, eventDict
from .libs import ObjDetection

class THIS_APIs(APIs):
    'The wrapper for all annotation APIs'
    def __init__(self, logger, socket):
      APIs.__init__(self, {
        'namespace': namespace,
        'logger': logger,
        'socket': socket,
        'events': eventDict,
        'package': package,
        'outputDir': outputDir
      })
      self.apiParms({
        'detector': ObjDetection()
      })
      self.start()
