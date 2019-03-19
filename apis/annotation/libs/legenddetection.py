"""The module for detecting color legends"""
import traceback
import math
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from .__settings__ import TESTING
from .image_processing import CV2PIL

GRAY_SCALE_LEVEL = 32
MARGIN = 3

def entropy(labels, base=None):
    """ Computes entropy of label distribution. """
    n_labels = len(labels)
    if n_labels <= 1:
        return 0
    value, counts = np.unique(labels, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)
    if n_classes <= 1:
        return 0
    ent = 0.
  # Compute entropy
    base = math.e if base is None else base
    for i in probs:
        ent -= i * math.log(i, base)
    return ent

def divide_by_threshold(array):
    """Find ranges with the value larger than the given threshold"""
    # Step 0: decide the threshold and the min_count
    min_count = 2
    # if array.size > 0:
    #     min_count = round(float(array.size) * GAP_PERSENTAGE)
    threshold = 0
    if array.size > 0:
        threshold = 0 #array.max() * THRES_PERSENTAGE
    # Step 1: divide the array by the given threshold
    empty_ranges = {}
    temp_range = {}
    # Step 1-1: find the empty ranges
    for _id, _value in enumerate(array):
        if _value <= threshold:
            if temp_range:
                temp_range["end"] = _id
                temp_range["length"] = temp_range["length"] + 1
            else:
                temp_range["start"] = _id
                temp_range["end"] = _id
                temp_range["length"] = 1
        elif temp_range:
            temp_range = {}
        if temp_range and temp_range["length"] >= min_count:
            range_head = temp_range["start"]
            if empty_ranges.get(range_head) is None:
                empty_ranges[range_head] = temp_range
    print(empty_ranges)
    # Step 1-2: find the non-empty ranges
    solid_ranges = {}
    temp_range = {}
    for _id, _value in enumerate(array):
        is_empty = False
        for empty_range in empty_ranges.values():
            if empty_range["start"] <= _id <= empty_range["end"]:
                is_empty = True
                break
        if not is_empty:
            if temp_range:
                temp_range["end"] = _id
                temp_range["length"] = temp_range["length"] + 1
            else:
                temp_range["start"] = _id
                temp_range["end"] = _id
                temp_range["length"] = 1
        else:
            temp_range = {}
        if temp_range and temp_range["length"] > 1:
            range_head = temp_range["start"]
            if solid_ranges.get(range_head) is None:
                solid_ranges[range_head] = temp_range
    print(solid_ranges)
    # Step 2: Decide which range belongs to the legend
    legend_range = None
    label_range = None
    if not (empty_ranges and solid_ranges):
        return legend_range, label_range
    range_values = list(solid_ranges.values())
    legend_range = range_values.pop(0)
    range_count = len(range_values)
    for range_id, range_value in enumerate(range_values):
        if label_range is None:
            label_range = range_value
        else:
            label_range["end"] = range_value["end"]
    label_range["length"] = label_range["end"] - label_range["start"] + 1
    return legend_range, label_range

def partition_legend(legend_img, legend_id):
    """Partition the legend image into two parts: legend and label"""
    # Initialize
    legend_array = None
    label_array = None
    legend_gray = cv2.cvtColor(legend_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    row_num = legend_img.shape[0]
    col_num = legend_img.shape[1]
    # Denoising: bilateral filtering
    # legend_gray = cv2.bilateralFilter(legend_img, 4, 50, 50)
    # Simplify the gray scales
    legend_array_simp = (legend_gray / GRAY_SCALE_LEVEL).astype(np.uint8)
    legend_array_simp = legend_array_simp * GRAY_SCALE_LEVEL
    row_ent = np.zeros(row_num)
    col_ent = np.zeros(col_num)
    for j in range(col_num):
        img_col = legend_array_simp[:, j].tolist()
        col_ent[j] = entropy(img_col)
    if TESTING['sign']:
        cv2.imwrite(TESTING['dir'] + '/legend_' + str(legend_id) + '.png', \
            legend_array_simp, \
            [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        np.savetxt(TESTING['dir'] + '/legend_' + str(legend_id) + '_col.txt', col_ent)
    # Step 2: divide the legend image
    legend_range, label_range = divide_by_threshold(row_ent)
    # Step 3: crop the legend image
    if legend_range:
        legend_start = legend_range["start"]
        legend_end = legend_range["end"]
        if legend_start >= MARGIN:
            legend_start = legend_start - MARGIN
        legend_array = legend_img[legend_start:legend_end, 0:col_num]
    if label_range:
        label_start = label_range["start"]
        label_end = label_range["end"]
        if label_start >= MARGIN:
            label_start = label_start - MARGIN
        label_array = legend_img[label_start:label_end, 0:col_num]
    if TESTING['sign']:
        if legend_array is not None:
            cv2.imwrite(TESTING['dir'] + '/legend_' + str(legend_id) + '_content.png', \
                legend_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        if label_array is not None:
            cv2.imwrite(TESTING['dir'] + '/legend_' + str(legend_id) + '_label.png', \
                label_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
    return legend_array, label_array

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
                            color_img, label_img = partition_legend(legend_img, legend_id)
                            if color_img is not None:
                                attrs.infer(color_img)
                            (color_img_w, color_img_h) = color_img.shape[:2]
                            mask_img = np.ones((color_img_h, color_img_w)).astype(np.uint8)
                            colors = attrs.get_mask_color(mask_img)
                            print(colors)
                            # Step 1: find the background color
                            max_score = float('-inf')
                            max_color = None
                            if colors:
                                for color in colors:
                                    c_score = float(colors[color])
                                    if c_score > max_score:
                                        max_color = color
                                        max_score = c_score
                                background_color = max_color
                                # Step 2: find the legend color
                                max_score = float('-inf')
                                max_color = None
                                for color in colors:
                                    if color == background_color:
                                        continue
                                    c_score = float(colors[color])
                                    if c_score > max_score:
                                        max_color = color
                                        max_score = c_score
                                legend_color = max_color
                                # Step 3: replace the legend color with the background color
                                # if legend_color is not None:
                                #     legend_img = cv2.cvtColor(legend_img, cv2.COLOR_BGR2GRAY)
                                #     # Find the background gray scale
                                #     counter = np.bincount(legend_img.flatten())
                                #     bg_gray = int(np.argmax(counter))
                                #     attrs.replace_color(legend_img, legend_color, bg_gray)
                                #     legend_img = cv2.cvtColor(legend_img, cv2.COLOR_GRAY2BGR)\
                                #         .astype(np.uint8)
                            # Step 4: scale up the legend image
                            (label_img_w, label_img_h) = label_img.shape[:2]
                            label_img = cv2.resize(label_img, (2*label_img_w, 2*label_img_h), \
                                interpolation=cv2.INTER_AREA)
                            img_pil = CV2PIL(label_img)
                            if TESTING["sign"]:
                                img_pil.save(TESTING['dir'] + '/legend_test_' + str(legend_id) + \
                                '.png')
                            legend_texts = pt.image_to_string(img_pil, config='--psm 6')
                            print((legend_x, legend_y), legend_texts, legend_color)
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
