"""The module for detecting color legends"""
import traceback
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from .__settings__ import TESTING
from .image_processing import CV2PIL

def get_format_legend(legend_color, legend_texts, legend_bbox, legend_score):
    """Pack the textual information of the axis"""
    legend = {}
    legend_range = {
        "x": [legend_bbox.get("x"), legend_bbox.get("x") + legend_bbox.get("width")],
        "y": [legend_bbox.get("y"), legend_bbox.get("y") + legend_bbox.get("height")]
    }
    legend["label"] = [legend_texts]
    legend["legend_data"] = {
        "color": legend_color
    }
    # make up the common object-detection data
    legend["class"] = "legend"
    legend["score"] = legend_score
    legend["color"] = {
        legend_color: 1.0
    }
    legend["bbox"] = legend_bbox
    legend["mask"] = [[
        [legend_range["x"][0], legend_range["y"][0]],
        [legend_range["x"][0], legend_range["y"][1]],
        [legend_range["x"][1], legend_range["y"][1]],
        [legend_range["x"][1], legend_range["y"][0]]
    ]]
    legend["position"] = {
        "x": (legend_range["x"][0] + legend_range["x"][1]) / 2,
        "y": (legend_range["y"][0] + legend_range["y"][1]) / 2
    }
    legend["size"] = {
        "area": legend_bbox.get("width") * legend_bbox.get("height"),
        "x_range": legend_range.get("x"),
        "y_range": legend_range.get("y")
    }
    return legend

def get_legend_info(img, attrs, legend_entities):
    """The function for getting the texts and colors in the legend"""
    try:
        data = []
        # No legends in the image
        if img is None or legend_entities is None:
            return data
        (img_height, img_width) = img.shape[:2]
        for legend_id, legend_entity in enumerate(legend_entities):
            legend_bbox = legend_entity.get("bbox")
            legend_score = legend_entity.get("score")
            legend_color = None
            if legend_bbox:
                legend_x = legend_bbox.get("x")
                legend_y = legend_bbox.get("y")
                legend_width = legend_bbox.get("width")
                legend_height = legend_bbox.get("height")
                if legend_x and legend_y and legend_width and legend_height:
                    if legend_x >= 0 and legend_y >= 0 and legend_width > 0 and legend_height > 0:
                        if img is not None and isinstance(img, np.ndarray):
                            legend_img = img[legend_y:(legend_y + legend_height), \
                                legend_x:(legend_x + legend_width)]
                            attrs.infer(legend_img)
                            mask_img = np.ones((legend_height, legend_width)).astype(np.uint8)
                            colors = attrs.get_mask_color(mask_img)
                            # Step 1: find the background color
                            max_score = float('-inf')
                            max_color = None
                            if colors:
                                for color, c_score in enumerate(colors):
                                    if c_score > max_score:
                                        max_color = color
                                background_color = max_color
                                # Step 2: find the legend color
                                max_score = float('-inf')
                                max_color = None
                                for color, c_score in enumerate(colors):
                                    if color == background_color:
                                        continue
                                    if c_score > max_score:
                                        max_color = color
                                legend_color = max_color
                                # Step 3: replace the legend color with the background color
                                if legend_color is not None:
                                    legend_img = cv2.cvtColor(legend_img, cv2.COLOR_BGR2GRAY)
                                    # Find the background gray scale
                                    counter = np.bincount(legend_img.flatten())
                                    bg_gray = int(np.argmax(counter))
                                    attrs.replace_color(legend_img, legend_color, bg_gray)
                                    legend_img = cv2.cvtColor(legend_img, cv2.COLOR_GRAY2BGR).astype(np.uint8)
                            img_pil = CV2PIL(legend_img)
                            if TESTING["sign"]:
                                img_pil.save(TESTING['dir'] + '/legend_' + str(legend_id) + \
                                '.png')
                            legend_texts = pt.image_to_string(img_pil, config='--psm 6')
                            print("label: ", legend_texts)
                            # legend_texts = pt.image_to_data(img_pil, config='--psm 6')
                            # legend_texts = understand_data(legend_texts)
                        if legend_texts is not None:
                            formated_legend = get_format_legend(legend_color, legend_texts, \
                                legend_bbox, legend_score)
                            data.append(formated_legend)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
    return data

    if title_array is not None:
        (h, w) = title_array.shape[:2]
        title_array = cv2.resize(title_array, (2*w, 2*h), interpolation=cv2.INTER_AREA)
