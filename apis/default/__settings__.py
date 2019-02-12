import os
from ..libs import API, APIs

# settings for this package
namespace = '/api'
package = 'apis.default'
outputDir = os.path.abspath('./files/default')

# message - apiName
eventDict = {
  'Hello': 'helloworld',
}