"""Pack the parameter results and return to client"""

class ODResultGenerator:
    """Pack the parameter results"""
    def __init__(self):
        self.score = None
        self.class_name = None
        self.bbox = None
        self.masks = None
        self.attrs = None
        self.clear_all()

    def clear_all(self):
        """Initialize the results"""
        self.get_score()
        self.get_class()
        self.get_bbox()
        self.get_mask()

    def get_score(self, score=-1):
        """Get the score of object detection"""
        self.score = score

    def get_class(self, class_name='undefined'):
        """Get the name of class"""
        self.class_name = class_name

    def get_bbox(self, box_x=0, box_y=0, box_width=0, box_height=0):
        """Get the bounding box"""
        self.bbox = {
            'x': box_x,
            'y': box_y,
            'width': box_width,
            'height': box_height
        }

    def get_mask(self, contours=None, attrs=None):
        """Get the contour with its attributes"""
        self.masks = contours
        self.attrs = attrs

    def pack(self):
        """Pack the final result"""
        result = {
            'class': self.class_name,
            'score': self.score,
            'bbox': self.bbox,
            'mask': self.masks,
            'color': self.attrs['color']
        }
        return result
        