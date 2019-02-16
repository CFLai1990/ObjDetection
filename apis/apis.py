"""Routing for all APIs"""
from .libs import Logger

# the default APIs
from .default import APIs as default_APIs
from .default import NAMESPACE as DEFAULT_NAMESPACE

# the default APIs
from .annotation import APIs as annotation_APIs
from .annotation import NAMESPACE as ANNOTATION_NAMESPACE

# the router dictionary
# namespace: apis
ROUTE_DICT = {
    DEFAULT_NAMESPACE: default_APIs,
    ANNOTATION_NAMESPACE: annotation_APIs,
}

class APIs:
    """The router for all APIs"""
    def __init__(self, logger, socket):
        # the APIs dictionary
        # namespace: apis_instance
        self.apis_dict = {}
        self.socket = socket
        self.logger = Logger('APIs', logger)
        self.route_by_namespace()
        self.logger.info('Server started')

    def route_by_namespace(self):
        """Route for each API namespace"""
        for namespace, apis in ROUTE_DICT.items():
            self.apis_dict[namespace] = apis(self.logger, self.socket)
