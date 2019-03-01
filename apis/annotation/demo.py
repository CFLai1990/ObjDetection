"""demo: take the image, return the masks"""
import base64
from .__settings__ import API
from .libs import NLPData, PIE

class ApiClass(API):
    """API Class"""
    def __init__(self, parameters):
        API.__init__(self, parameters)
        self.obj_detector = parameters['detector']

    def save_image(self, obj):
        """Save the original image"""
        img_path = self.file_op.get_path(obj['name'])
        with open(img_path, 'wb') as file:
            file.write(base64.b64decode(obj['data']))
            file.close()
        return img_path

    def od_mask(self, obj):
        """Run object detection, return the parameters"""
        # Save the original image
        img_path = self.save_image(obj)
        self.logger.info('Image saved')
        # Return the fake data for demo images
        data = []
        auxiliary = []
        if obj['name'] == 'demo_pie.png':
            data = PIE
        # Get the data for the NLP module
        nlp_parser = NLPData(data)
        tonlp = nlp_parser.get_result()
        # Pack the final result
        result = {
            'data': data,
            'auxiliary': auxiliary,
            'tonlp': tonlp
        }
        self.logger.info('Image detection finished')
        return result

    def execute(self, data):
        """Main function"""
        result = self.od_mask(data)
        self.emit2client(result)
        self.logger.info('Result sent')
