"""Get the label dictionary for vis images"""
from detectron.utils.collections import AttrDict

def get_vis_dict():
    """The dataset that includes all the 'classes' field."""
    ds_dict = AttrDict()
    classes = [
        '__ignore__', '_background_', 'rectangle', 'axis', 'legend', 'sector', 'circle'
    ]
    ds_dict.classes = {i: name for i, name in enumerate(classes)}
    return ds_dict

FIX_DICT = ['sector']
