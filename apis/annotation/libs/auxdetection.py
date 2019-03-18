"""Auxiliary Detection"""
import traceback
import cv2
import logging
from .axisdetection import get_axes_texts

class AuxDetection:
    """Auxiliary Entity Detection Class"""
    def __init__(self):
        self.logger = logging.getLogger('ObjDetection')
        self.aux = []
        self.axes = None
        self.legends = None

    def infer_parameters(self, img_path, data_entities):
        """Get the auxiliary data in the vis image"""
        try:
            self.aux = []
            img = cv2.imread(img_path)
            if img is not None:
                self.get_legends(img, data_entities)
                self.get_axes(img, data_entities)
        except Exception as e:
            print(repr(e))
            traceback.print_exc()
        return self.aux

    def get_legends(self, img, data_entities):
        """Get the color legends in the vis image"""
        self.legends = []
        if self.legends:
            for legend in self.legends:
                self.aux.append(legend)

    def get_axis_info(self, data_entity):
        """Get the direction of an axis"""
        direction = None
        bbox = data_entity.get("bbox") or {}
        if bbox:
            axis_x = bbox.get("x")
            axis_y = bbox.get("y")
            axis_width = bbox.get("width")
            axis_height = bbox.get("height")
            if axis_x and isinstance(axis_x, float) and axis_y and isinstance(axis_y, float):
                axis_x = round(axis_x)
                axis_y = round(axis_y)
            if axis_width and isinstance(axis_width, float) and axis_height and isinstance(axis_height, float):
                axis_width = round(axis_width)
                axis_height = round(axis_height)
                if axis_width >= 0 and axis_height >= 0:
                    direction = 0
                    if axis_width < axis_height:
                        direction = 90
            bbox = {
                "x": axis_x,
                "y": axis_y,
                "width": axis_width,
                "height": axis_height
            }
        return {
            "score": data_entity.get("score"),
            "bbox": bbox,
            "direction": direction
        }

    def get_axes(self, img, data_entities):
        """Get the axis in the vis image"""
        # Get the data entities with classname "axis"
        axes_entities = []
        axes_indices = []
        if data_entities:
            for entity_id, data_entity in enumerate(data_entities):
                entity_class = data_entity.get("class")
                if entity_class and entity_class == "axis":
                    axes_indices.append(entity_id)
            axes_indices.reverse()
            for axis_id in axes_indices:
                axis_entity = data_entities.pop(axis_id)
                axis_entity = self.get_axis_info(axis_entity)
                axes_entities.append(axis_entity)
        self.axes = get_axes_texts(img, axes_entities)
        if self.axes:
            for axis in self.axes:
                self.aux.append(axis)
