"""The module for detecting axes"""
import math
from PIL import Image
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from sklearn.cluster import KMeans
from .__settings__ import TS_LANG, TESTING

GRAY_SCALE_LEVEL = 128
MARGIN = 3

def PIL2CV(img_PIL):
    """Convert a PIL image to a CV2 image"""
    return cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)

def CV2PIL(img_CV):
    """Convert a CV2 image to a PIL image"""
    return Image.fromarray(cv2.cvtColor(img_CV, cv2.COLOR_BGR2RGB))

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

def understand_data(data):
    """Parse the pytesseract data"""
    lines = data.split("\n")
    items = []
    head = lines[0].split("\t")
    for k, line in enumerate(lines):
        if k == 0:
            continue
        item = {}
        attributes = line.split("\t")
        if len(head) != len(attributes):
            continue
        # assert len(head) == len(attributes), "Oops, the head number is not equal to the attributes number of this item"
        for i, attr in enumerate(attributes):
            item[head[i]] = attr
        if item["text"] != " " and item["text"] != "":
            item["width"] = int(item['width'])
            item["top"] = int(item['top'])
            item["left"] = int(item['left'])
            item["height"] = int(item['height'])
            item["conf"] = int(item["conf"])
            items.append(item)
    return items

def classify_texts(direction, f_items, ticks, labels):
    """The function for classifying ticks and labels"""
    proj_positions = []
    vertical_direction = (direction + 90) / 180 * math.pi
    vec_len = 10
    vertical_vector = {
        "x": vec_len * math.cos(vertical_direction),
        "y": vec_len * math.sin(vertical_direction)
    }
    # Project to the vertical direction
    for f_item in f_items:
        pos = f_item.get("position")
        proj_pos = [pos.get("x") * vertical_vector.get("x") + pos.get("y") * vertical_vector.get("y")]
        proj_positions.append(proj_pos)
    proj_data = np.array(proj_positions)
    # Classify based on the projected positions
    estimator = KMeans(n_clusters=2)
    estimator.fit(proj_data)
    label_pred = estimator.labels_
    classes = {}
    for i in range(len(f_items)):
        label_i = label_pred[i]
        class_i = classes.get(label_i)
        if class_i is None:
            classes[label_i] = [i]
        else:
            class_i.append(i)
    # Assume that there are more ticks texts than the label texts
    tick_class = None
    label_class = None
    if len(classes.get(0)) > len(classes.get(1)):
        tick_class = classes.get(0)
        label_class = classes.get(1)
    else:
        tick_class = classes.get(1)
        label_class = classes.get(0)
    # Pack the results
    for tick_i in tick_class:
        ticks.append(f_items[tick_i])
    for label_i in label_class:
        labels.append(f_items[label_i]["text"])

def get_format_axis(items, axis_bbox, axis_direction):
    """Pack the textual information of the axis"""
    axis = {}
    axis_range = {
        "x": [axis_bbox.get("x"), axis_bbox.get("x") + axis_bbox.get("width")],
        "y": [axis_bbox.get("y"), axis_bbox.get("y") + axis_bbox.get("height")]
    }
    ticks = []
    labels = []
    format_items = []
    for item in items:
        item_text = item.get("text")
        if item_text in ("-", ""):
            continue
        format_item = {}
        if item_text[-1] == "-":
            item_text = item_text[:-1]
        format_item["text"] = item_text
        bbox = {
            "x": item["left"] + axis_bbox.get("x"),
            "y": item["top"] + axis_bbox.get("y"),
            "width": item.get("width"),
            "height": item.get("height")
        }
        format_item["bbox"] = bbox
        position = {
            "x": bbox["x"] + bbox["width"] / 2,
            "y": bbox["y"] + bbox["height"] / 2
        }
        format_item["position"] = position
        if format_item["text"] != "":
            format_items.append(format_item)
    # Classify if the texts belong to the ticks or the label
    classify_texts(axis_direction, format_items, ticks, labels)
    axis["label"] = " ".join(labels)
    axis["axis_data"] = {
        "ticks": ticks,
        "direction": axis_direction
    }
    # make up the common object-detection data
    axis["class"] = "axis"
    axis["score"] = 0.9
    axis["color"] = {"white": 0.8, "black": 0.2}
    axis["bbox"] = axis_bbox
    axis["mask"] = [[
        [axis_range["x"][0], axis_range["y"][0]],
        [axis_range["x"][0], axis_range["y"][1]],
        [axis_range["x"][1], axis_range["y"][1]],
        [axis_range["x"][1], axis_range["y"][0]]
    ]]
    axis["position"] = {
        "x": (axis_range["x"][0] + axis_range["x"][1]) / 2,
        "y": (axis_range["y"][0] + axis_range["y"][1]) / 2
    }
    axis["size"] = {
        "area": axis_bbox.get("width") * axis_bbox.get("height"),
        "x_range": axis_range.get("x"),
        "y_range": axis_range.get("y")
    }
    return axis

def divide_by_threshold(array, threshold, min_count=1):
    """Find ranges with the value larger than the given threshold"""
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
    # Step 2: Decide which range belongs to which category
    line_range = None
    tick_range = None
    title_range = None
    if not (empty_ranges and solid_ranges):
        return line_range, tick_range, title_range
    range_values = list(solid_ranges.values())
    range_count = len(range_values)
    # Case 1: only the ticks
    if range_count == 1:
        tick_range = range_values[0]
    # Case 2: line + tick or line + tick + title
    elif range_count > 0:
        min_range_len = float('Inf')
        min_range_id = -1
        # Assume the line to be the smallest range
        for range_id, range_value in enumerate(range_values):
            if range_value["length"] < min_range_len:
                min_range_len = range_value["length"]
                min_range_id = range_id
        if min_range_id >= 0:
            line_range = range_values.pop(min_range_id)
        # Find the range closest to the line
        if line_range:
            min_dist = float('Inf')
            min_dist_id = -1
            for range_id, range_value in enumerate(range_values):
                dist = min(\
                    abs(range_value["start"] - line_range["start"]), \
                    abs(range_value["start"] - line_range["end"]), \
                    abs(range_value["end"] - line_range["start"]), \
                    abs(range_value["end"] - line_range["end"]))
                if dist < min_dist:
                    min_dist = dist
                    min_dist_id = range_id
            if min_dist_id >= 0:
                tick_range = range_values.pop(min_dist_id)
            # If there are still ranges left, it must be the title
            if range_values:
                title_range = range_values[0]
    return line_range, tick_range, title_range

def partition_axis(axis_img, axis_id, axis_direction):
    """Partition the axis image into three parts: line, tick_texts and title"""
    line_array = None
    tick_array = None
    title_array = None
    # Initialize
    print("Step 1")
    axis_array = cv2.cvtColor(axis_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    row_num = axis_array.shape[0]
    col_num = axis_array.shape[1]
    # Simplify the gray scales
    print(row_num, col_num)
    print("Step 2")
    axis_array_simp = (axis_array / GRAY_SCALE_LEVEL).astype(np.uint8)
    axis_array_simp = axis_array_simp * GRAY_SCALE_LEVEL
    # Calculate the entropy of the simplified image
    print("Step 3")
    row_ent = np.zeros(row_num)
    col_ent = np.zeros(col_num)
    for i in range(row_num):
        img_row = axis_array_simp[i].tolist()
        row_ent[i] = entropy(img_row)
    for j in range(col_num):
        img_col = axis_array_simp[:, j].tolist()
        col_ent[j] = entropy(img_col)
    print("Step 4")
    if TESTING['sign']:
        cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '.png', \
            axis_array_simp, \
            [int(cv2.IMWRITE_PNG_COMPRESSION),0])
        np.savetxt(TESTING['dir'] + '/axis_' + str(axis_id) + '_row.txt', row_ent)
        np.savetxt(TESTING['dir'] + '/axis_' + str(axis_id) + '_col.txt', col_ent)
    print("Step 5")
    # Step 1: transform the image into a gray one
    axis_array = cv2.cvtColor(axis_array, cv2.COLOR_GRAY2BGR)
    print("axis_array: ", axis_array)
    if axis_direction == 0:
        # Step 2: divide the axis image
        line_range, tick_range, title_range = divide_by_threshold(row_ent, 0, 3)
        # Step 3: crop the axis image
        if line_range:
            print("line: ", line_range["start"], line_range["end"], 0, col_num)
            line_array = axis_array[line_range["start"]:line_range["end"], 0:col_num]
        if tick_range:
            tick_start = tick_range["start"]
            tick_end = tick_range["end"]
            if tick_start >= MARGIN:
                tick_start = tick_start - MARGIN
            if tick_end <= row_num - MARGIN:
                tick_end = tick_end + MARGIN
            print("tick: ", tick_start, tick_end, 0, col_num)
            tick_array = axis_array[tick_start:tick_end, 0:col_num]
        if title_range:
            title_start = title_range["start"]
            title_end = title_range["end"]
            if title_start >= MARGIN:
                title_start = title_start - MARGIN
            if title_end <= row_num - MARGIN:
                title_end = title_end + MARGIN
            print("title: ", title_start, title_end, 0, col_num)
            title_array = axis_array[title_start:title_end, 0:col_num]
    elif axis_direction == 90:
        # Step 2: divide the axis image
        line_range, tick_range, title_range = divide_by_threshold(col_ent, 0, 3)
        # Step 3: crop the axis image
        if line_range:
            print("line: ", 0, row_num, line_range["start"], line_range["end"])
            line_array = axis_array[0:row_num, line_range["start"]:line_range["end"]]
        if tick_range:
            tick_start = tick_range["start"]
            tick_end = tick_range["end"]
            if tick_start >= MARGIN:
                tick_start = tick_start - MARGIN
            if tick_end <= col_num - MARGIN:
                tick_end = tick_end + MARGIN
            print("tick: ", 0, row_num, tick_start, tick_end)
            tick_array = axis_array[0:row_num, tick_start:tick_end]
        if title_range:
            title_start = title_range["start"]
            title_end = title_range["end"]
            if title_start >= MARGIN:
                title_start = title_start - MARGIN
            if title_end <= col_num - MARGIN:
                title_end = title_end + MARGIN
            print("title: ", 0, row_num, title_start, title_end)
            title_array = axis_array[0:row_num, title_start:title_end]
    print("line_array: ", line_array.shape)
    print("tick_array: ", tick_array.shape)
    print("title_array: ", title_array.shape)
    print("Step 6")
    if TESTING['sign']:
        if line_array:
            cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '_line.png', \
                line_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION),0])
        if tick_array:
            cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '_tick.png', \
                tick_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION),0])
        if title_array:
            cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '_title.png', \
                title_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION),0])
    return line_array, tick_array, title_array

def contrast_enhance(axis_img):
    """Enhance the contrast of the axis image"""
    lab= cv2.cvtColor(axis_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img

def get_axes_texts(img, axis_entities):
    """The function for getting the texts in the axis"""
    data = []
    # No axes in the image
    if img is None or axis_entities is None:
        return data
    axis_id = 0
    for axis_entity in axis_entities:
        axis_bbox = axis_entity.get("bbox")
        axis_direction = axis_entity.get("direction")
        if axis_bbox:
            axis_x = axis_bbox.get("x")
            axis_y = axis_bbox.get("y")
            axis_width = axis_bbox.get("width")
            axis_height = axis_bbox.get("height")
            if axis_x and axis_y and axis_width and axis_height:
                if axis_x >= 0 and axis_y >= 0 and axis_width > 0 and axis_height > 0:
                    # Step 1: crop the axis image
                    axis_img = img[axis_y:(axis_y + axis_height), axis_x:(axis_x + axis_width)]
                    # Step 2: enhance the contrast
                    axis_img_enhanced = contrast_enhance(axis_img)
                    # Step 3: partition the image
                    line_img, tick_img, title_img = partition_axis(axis_img_enhanced, axis_id, axis_direction)
                    print("finished")
                    tick_info = {}
                    title_info = {}
                    if tick_img:
                        tick_img_pil = CV2PIL(tick_img)
                        tick_texts = pt.image_to_data(tick_img_pil)
                        print("tick_texts (before): ", tick_texts)
                        tick_texts = understand_data(tick_texts)
                        print("tick_texts (after): ", tick_texts)
                    if title_img:
                        title_img_pil = CV2PIL(title_img)
                        title_texts = pt.image_to_data(title_img_pil)
                        print("title_texts (before): ", title_texts)
                        title_texts = understand_data(title_texts)
                        print("tick_texts (after): ", tick_texts)
                    # axis_texts = pt.image_to_data(axis_img, lang=TS_LANG)
                    # axis_texts = understand_data(axis_texts)
                    # formated_axis = get_format_axis(axis_texts, axis_bbox, axis_direction)
                    # data.append(formated_axis)
                    axis_id = axis_id + 1
    return data
