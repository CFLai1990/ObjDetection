"""The default APIs"""
from .__settings__ import APIs, NAMESPACE, PACKAGE, OUTPUT_DIR, EVENT_DICT

class THISAPIs(APIs):
    """The wrapper for all default APIs"""
    def __init__(self, logger, socket):
        APIs.__init__(self, {
            'namespace': NAMESPACE,
            'logger': logger,
            'socket': socket,
            'events': EVENT_DICT,
            'package': PACKAGE,
            'output_dir': OUTPUT_DIR
        })
        self.start()
