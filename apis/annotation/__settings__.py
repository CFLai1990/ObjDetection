"""annotation APIs: __settings__"""
import os
from ..libs import API, APIs

# settings for this package
NAMESPACE = '/api/annotation'
PACKAGE = 'apis.annotation'
OUTPUT_DIR = os.path.abspath('./files/annotation')
INFER_SIGN = True

# message - apiName
EVENT_DICT = {
    'OD_Image': 'odimg',
    'OD_Mask': 'odmsk',
    'OD_Test': 'odtest',
    'OD_Demo': 'demo'
}
