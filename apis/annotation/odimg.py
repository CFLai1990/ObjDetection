"""odimg: take the image, return the masked image"""
import base64
from .__settings__ import API

class ApiClass(API):
    """API Class"""
    def __init__(self, parameters):
        API.__init__(self, parameters)
        self.obj_detector = parameters['obj_detector']

    def save_image(self, obj):
        """Save the original image"""
        img_path = self.file_op.get_path(obj['name'])
        with open(img_path, 'wb') as file:
            file.write(base64.b64decode(obj['data']))
            file.close()
        return img_path

    def load_image(self, path):
        """Load the masked image"""
        with open(path, 'rb') as file:
            img_base64 = str(base64.b64encode(file.read()), 'utf-8') # for Python 3
            file.close()
        return img_base64

    def od_image(self, obj):
        """Run object detection, return the masked image"""
        # Save the original image
        img_path = self.save_image(obj)
        self.logger.info('Image saved')
        # Object detection
        ext_type = obj['type']
        img_type = self.file_op.get_type(ext_type)
        output_dir = self.file_op.get_root()
        output_path = self.obj_detector.infer_image(img_path, img_type, output_dir)
        self.logger.info('Image detection finished')
        # Load the processed image
        output_name = self.file_op.get_name(output_path)
        img_data = self.load_image(output_path)
        result = {
            'name': output_name,
            'type': ext_type,
            'data': img_data,
        }
        return result

    def execute(self, data):
        """Main function"""
        result = self.od_image(data)
        self.emit2client(result)
        self.logger.info('Result sent')
