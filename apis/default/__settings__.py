"""default APIs: __settings__"""
import os
from ..libs import API, APIs

# settings for this package
NAMESPACE = '/api'
PACKAGE = 'apis.default'
OUTPUT_DIR = os.path.abspath('./files/default')

# message - apiName
EVENT_DICT = {
    'Hello': 'helloworld',
}
