"""Pack the parameter results and return to client"""

class ODResultGenerator:
    """Pack the parameter results"""
    def __init__(self):
        self.score = None
        self.class_name = None
        self.fix_bbox = False
        self.bbox = None
        self.masks = None
        self.attrs = None
        self.label = []
        self.clear_all()

    def clear_all(self):
        """Initialize the results"""
        self.get_score()
        self.get_class()
        self.get_mask()
        self.get_bbox()
        self.get_label()

    def get_score(self, score=-1):
        """Get the score of object detection"""
        self.score = score

    def get_class(self, class_name='undefined'):
        """Get the name of class"""
        self.class_name = class_name

    def get_bbox(self, box_x=0, box_y=0, box_width=0, box_height=0):
        """Get the bounding box"""
        bbox = None
        if self.fix_bbox:
            masks = self.masks
            x_min = float("inf")
            x_max = float("-inf")
            y_min = float("inf")
            y_max = float("-inf")
            if self.masks:
                for mask in self.masks:
                    if mask:
                        for vertex in mask:
                            if vertex[0] < x_min:
                                x_min = vertex[0]
                            if vertex[0] > x_max:
                                x_max = vertex[0]
                            if vertex[1] < y_min:
                                y_min = vertex[1]
                            if vertex[1] > y_max:
                                y_max = vertex[1]
                bbox = {
                    'x': x_min,
                    'y': y_min,
                    'width': x_max - x_min,
                    'height': y_max - y_min
                }
        else:
            bbox = {
                'x': round(box_x),
                'y': round(box_y),
                'width': round(box_width),
                'height': round(box_height)
            }
        self.bbox = bbox
        return bbox

    def get_mask(self, contours=None, attrs=None):
        """Get the contour with its attributes"""
        self.masks = contours
        self.attrs = attrs

    def get_label(self, label=None):
        """Get the label of the entity"""
        if label is not None:
            self.label = label

    def pack(self):
        """Pack the final result"""
        result = {
            'class': self.class_name,
            'score': self.score,
            'label': self.label,
            'bbox': self.bbox,
            'mask': self.masks,
            'color': self.attrs.get('color'),
            'color_rgb': self.attrs.get('color_rgb'),
            'size': self.attrs.get('size'),
            'position': self.attrs.get('position')
        }
        return result
        