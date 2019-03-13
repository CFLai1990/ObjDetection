"""Auxiliary Detection"""
import logging
from .get_axis import get_axis

class AuxDetection:
    """Auxiliary Entity Detection Class"""
    def __init__(self):
        self.logger = logging.getLogger('ObjDetection')
        self.aux = []
        self.axes = None
        self.legends = None

    def infer_parameters(self, img_path, data_entities):
        """Get the auxiliary data in the vis image"""
        self.get_legends(img_path, data_entities)
        self.get_axes(img_path, data_entities)
        return self.aux

    def get_legends(self, img_path, data_entities):
        """Get the color legends in the vis image"""
        self.legends = []
        if self.legends:
            for legend in self.legends:
                self.aux.append(legend)

    def get_axes(self, img_path, data_entities):
        """Get the axis in the vis image"""
        self.axes = get_axis(img_path)
        print(type(self.axes))
        if self.axes:
            for axis in self.axes:
                print(axis)
                self.aux.append(axis)
