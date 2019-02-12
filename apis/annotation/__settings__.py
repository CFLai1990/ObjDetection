import os
from ..libs import API, APIs

# settings for this package
namespace = '/api/annotation'
package = 'apis.annotation'
outputDir = os.path.abspath('./files/annotation')

# message - apiName
eventDict = {
  'OD_Image': 'odimg',
  'OD_Mask': 'odmsk'
}