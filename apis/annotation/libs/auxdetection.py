"""Auxiliary Detection"""
import logging
from .axisdetection import get_axis_texts

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

    def get_axis_info(self, data_entity):
        """Get the direction of an axis"""
        direction = None
        bbox = data_entity.get("bbox")
        if bbox:
            axis_width = bbox.get("width")
            axis_height = bbox.get("height")
            if axis_width and axis_height and axis_width > 0 and axis_height > 0:
                direction = 0
                if axis_width < axis_height:
                    direction = 90
        return {
            "bbox": bbox,
            "direction": direction
        }

    def get_axes(self, img_path, data_entities):
        """Get the axis in the vis image"""
        # Get the data entities with classname "axis"
        axes_entities = []
        if data_entities:
            for entity_id, data_entity in enumerate(data_entities):
                if data_entity.get("class") == "axis":
                    data_entities.pop(entity_id)
                    axis_entity = self.get_axis_info(data_entity)
                    axes_entities.append(axis_entity)
        self.axes = get_axis_texts(img_path, axes_entities)
        if self.axes:
            for axis in self.axes:
                self.aux.append(axis)
