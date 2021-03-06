"""odmsk: take the image, return the masks"""
import traceback
import base64
from .__settings__ import API, INFER_SIGN
from .libs import NLPData

class ApiClass(API):
    """API Class"""
    def __init__(self, parameters):
        API.__init__(self, parameters)
        self.obj_detector = parameters['obj_detector']
        self.aux_detector = parameters['aux_detector']

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
        # Object detection
        if INFER_SIGN:
            data = self.obj_detector.infer_parameters(img_path)
        else:
            data = None
        auxiliary = self.aux_detector.infer_parameters(img_path, data)
        # Get the data for the NLP module
        nlp_parser = NLPData(data, auxiliary)
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
        try:
            result = self.od_mask(data)
            self.emit2client(result)
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
        self.logger.info('Result sent')
