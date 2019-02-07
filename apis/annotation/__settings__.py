import os
from ..libs import API, Logger

# settings for this package
namespace = '/api/annotation'
packageName = 'apis.annotation'
filePath = os.path.abspath('./files/annotation')
fileType = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
}