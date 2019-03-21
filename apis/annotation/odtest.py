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

    def load_image(self, path):
        """Load the masked image"""
        output_name = None
        if path is not None:
            output_name = self.file_op.get_name(path)
        with open(path, 'rb') as file:
            img_base64 = str(base64.b64encode(file.read()), 'utf-8') # for Python 3
            file.close()
        return output_name, img_base64

    def parse_info(self, obj):
        """Get the information of the saved image"""
        ext_type = obj.get('type')
        img_type = self.file_op.get_type(ext_type)
        output_dir = self.file_op.get_root()
        return ext_type, img_type, output_dir

    def od_mask(self, obj):
        """Run object detection, return the parameters"""
        # Save the original image
        img_path = self.save_image(obj)
        self.logger.info('Image saved')
        # Parse the information of the image
        ext_type, img_type, output_dir = self.parse_info(obj)
        # Object detection
        if INFER_SIGN:
            output_path, data = self.obj_detector.infer_image_with_parameters(img_path, \
                img_type, output_dir)
        else:
            output_path = None
            data = None
        auxiliary = self.aux_detector.infer_parameters(img_path, data)
        # Load the processed image
        output_name, img_data = self.load_image(output_path)
        # Get the data for the NLP module
        nlp_parser = NLPData(data, auxiliary)
        tonlp = nlp_parser.get_result()
        # Pack the final result
        result_image = {
            'name': output_name,
            'type': ext_type,
            'data': img_data,
        }
        result_data = {
            'data': data,
            'auxiliary': auxiliary,
            'tonlp': tonlp
        }
        self.logger.info('Image detection finished')
        return {
            "image": result_image,
            "data": result_data
        }

    def execute(self, data):
        """Main function"""
        try:
            result = self.od_mask(data)
            self.emit2client(result)
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
        self.logger.info('Result sent')
