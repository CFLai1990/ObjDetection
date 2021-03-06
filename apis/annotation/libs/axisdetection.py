"""The module for detecting axes"""
import traceback
import math
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from sklearn.cluster import KMeans
from .__settings__ import TESTING
from .image_processing import CV2PIL, contrast_enhance

GRAY_SCALE_LEVEL = 64
GRAY_SCALE_BINARY = 128
GRAY_RANGE = 10
GAP_PERSENTAGE = 0.04
SCALE_DEGREE = 2
MINI_TICK_EXTRA = 2
THRES_PERSENTAGE = 0
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

def get_format_axis(ticks_data, label_texts, ticks_bbox, img_shape, axis_bbox, axis_direction, axis_score):
    """Pack the textual information of the axis"""
    axis = {}
    axis_range = {
        "x": [axis_bbox.get("x"), axis_bbox.get("x") + axis_bbox.get("width")],
        "y": [axis_bbox.get("y"), axis_bbox.get("y") + axis_bbox.get("height")]
    }
    ticks = []
    tick_range = {
        "x": 0,
        "y": 0,
        "width": 0,
        "height": 0
    }
    if ticks_bbox is not None:
        tick_range = ticks_bbox.copy()
    # format_items = []
    for tick_data in ticks_data:
        item_text = tick_data.get("text")
        tick = {}
        tick["text"] = item_text
        if TESTING["axis"]["sign"]:
            print("---------------------------------------")
            print("tick_data: ", tick_data)
            print("axis_bbox: ", axis_bbox)
            print("tick_range: ", tick_range)
            print("---------------------------------------")
        tick_bbox = {
            "x": round(tick_data["left"] / SCALE_DEGREE) + tick_range.get("x") + axis_bbox.get("x"),
            "y": round(tick_data["top"] / SCALE_DEGREE) + tick_range.get("y") + axis_bbox.get("y"),
            "width": round(tick_data.get("width") / SCALE_DEGREE),
            "height": round(tick_data.get("height") / SCALE_DEGREE)
        }
        if (tick_bbox["x"] > MINI_TICK_EXTRA) and\
            (tick_bbox["x"] + tick_bbox["width"] + MINI_TICK_EXTRA < img_shape["width"]):
            tick_bbox["x"] = tick_bbox["x"] - MINI_TICK_EXTRA
            tick_bbox["width"] = tick_bbox["width"] + 2 * MINI_TICK_EXTRA
        if (tick_bbox["y"] > MINI_TICK_EXTRA) and\
            (tick_bbox["y"] + tick_bbox["height"] + MINI_TICK_EXTRA < img_shape["height"]):
            tick_bbox["y"] = tick_bbox["y"] - MINI_TICK_EXTRA
            tick_bbox["height"] = tick_bbox["height"] + 2 * MINI_TICK_EXTRA
        tick["bbox"] = tick_bbox
        position = {
            "x": tick_bbox["x"] + tick_bbox["width"] / 2,
            "y": tick_bbox["y"] + tick_bbox["height"] / 2
        }
        tick["position"] = position
        if tick["text"] != "":
            ticks.append(tick)
            # format_items.append(tick)
    # Classify if the texts belong to the ticks or the label
    # classify_texts(axis_direction, format_items, ticks, labels)
    axis_label = label_texts
    if isinstance(axis_label, list):
        axis_label = " ".join(axis_label)
    axis["label"] = axis_label
    axis["axis_data"] = {
        "ticks": ticks,
        "direction": axis_direction
    }
    # make up the common object-detection data
    axis["class"] = "axis"
    axis["score"] = axis_score
    axis["color"] = None
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

def divide_by_threshold(array):
    """Find ranges with the value larger than the given threshold"""
    # Step 0: decide the threshold and the min_count
    min_count = 3
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
    ticks_bbox = None
    # Initialize
    axis_array = cv2.cvtColor(axis_img, cv2.COLOR_BGR2GRAY).astype(np.uint8)
    row_num = axis_array.shape[0]
    col_num = axis_array.shape[1]
    # Denoising: bilateral filtering
    axis_array_smooth = cv2.bilateralFilter(axis_array, 4, 50, 50)
    # Simplify the gray scales
    axis_array_simp = (axis_array_smooth / GRAY_SCALE_LEVEL).astype(np.uint8)
    axis_array_simp = axis_array_simp * GRAY_SCALE_LEVEL
    # axis_array_simp[(axis_array > bg_gray - GRAY_RANGE) \
    # & (axis_array < bg_gray + GRAY_RANGE)] = bg_gray
    # Calculate the entropy of the simplified image
    row_ent = np.zeros(row_num)
    col_ent = np.zeros(col_num)
    for i in range(row_num):
        img_row = axis_array_simp[i].tolist()
        row_ent[i] = entropy(img_row)
    for j in range(col_num):
        img_col = axis_array_simp[:, j].tolist()
        col_ent[j] = entropy(img_col)
    if TESTING["axis"]["sign"]:
        cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '.png', \
            axis_array_simp, \
            [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        np.savetxt(TESTING['dir'] + '/axis_' + str(axis_id) + '_row.txt', row_ent)
        np.savetxt(TESTING['dir'] + '/axis_' + str(axis_id) + '_col.txt', col_ent)
    # Step 1: transform the image into a gray one
    axis_array = cv2.cvtColor(axis_array, cv2.COLOR_GRAY2BGR)
    # Step 1-1: prepare the binary image
    # axis_array_smooth = (axis_array / GRAY_SCALE_BINARY).astype(np.uint8)
    # axis_array_smooth = axis_array_smooth * GRAY_SCALE_BINARY
    # axis_array_smooth[axis_array_smooth == 128] = 255
    # Smoothing
    # axis_array_smooth = cv2.bilateralFilter(axis_array, 4, 50, 50)
    if axis_direction == 0:
        # Step 2: divide the axis image
        line_range, tick_range, title_range = divide_by_threshold(row_ent)
        # Step 3: crop the axis image
        if line_range:
            line_array = axis_array_smooth[line_range["start"]:line_range["end"], 0:col_num]
        if tick_range:
            tick_start = tick_range["start"]
            tick_end = tick_range["end"]
            if tick_start >= MARGIN:
                tick_start = tick_start - MARGIN
            if tick_end <= row_num - MARGIN:
                tick_end = tick_end + MARGIN
            tick_array = axis_array_smooth[tick_start:tick_end, 0:col_num]
            ticks_bbox = {
                "x": 0,
                "y": tick_start,
                "width": col_num,
                "height": tick_end - tick_start + 1
            }
        if title_range:
            title_start = title_range["start"]
            title_end = title_range["end"]
            if title_start >= MARGIN:
                title_start = title_start - MARGIN
            if title_end <= row_num - MARGIN:
                title_end = title_end + MARGIN
            title_array = axis_array_smooth[title_start:title_end, 0:col_num]
        if TESTING["axis"]["sign"]:
            print("direction: 0")
            print("line_range: ", line_range)
            print("tick_range: ", tick_range)
            print("title_range: ", title_range)
    elif axis_direction == 90:
        # Step 2: divide the axis image
        line_range, tick_range, title_range = divide_by_threshold(col_ent)
        # Step 3: crop the axis image
        if line_range:
            line_array = axis_array_smooth[0:row_num, line_range["start"]:line_range["end"]]
        if tick_range:
            tick_start = tick_range["start"]
            tick_end = tick_range["end"]
            if tick_start >= MARGIN:
                tick_start = tick_start - MARGIN
            if tick_end <= col_num - MARGIN:
                tick_end = tick_end + MARGIN
            tick_array = axis_array_smooth[0:row_num, tick_start:tick_end]
            ticks_bbox = {
                "x": tick_start,
                "y": 0,
                "width": tick_end - tick_start + 1,
                "height": row_num,
            }
        if title_range:
            title_start = title_range["start"]
            title_end = title_range["end"]
            if title_start >= MARGIN:
                title_start = title_start - MARGIN
            if title_end <= col_num - MARGIN:
                title_end = title_end + MARGIN
            title_array = axis_array_smooth[0:row_num, title_start:title_end]
            # Assume the title should be rotated clockwise for 90 degrees
            title_array = np.rot90(title_array, 3)
        if TESTING["axis"]["sign"]:
            print("direction: 90")
            print("line_range: ", line_range)
            print("tick_range: ", tick_range)
            print("title_range: ", title_range)
    # Scale the images in case the dpi is too low for detection
    if tick_array is not None:
        (h, w) = tick_array.shape[:2]
        tick_array = cv2.resize(tick_array, (SCALE_DEGREE * w, SCALE_DEGREE * h), interpolation=cv2.INTER_AREA)
    if title_array is not None:
        (h, w) = title_array.shape[:2]
        title_array = cv2.resize(title_array, (SCALE_DEGREE * w, SCALE_DEGREE * h), interpolation=cv2.INTER_AREA)
    if TESTING["axis"]["sign"]:
        if line_array is not None:
            cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '_line.png', \
                line_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        if tick_array is not None:
            cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '_tick.png', \
                tick_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        if title_array is not None:
            cv2.imwrite(TESTING['dir'] + '/axis_' + str(axis_id) + '_title.png', \
                title_array, \
                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
    return line_array, tick_array, title_array, ticks_bbox

def get_axes_texts(img, axis_entities):
    """The function for getting the texts in the axis"""
    try:
        data = []
        # No axes in the image
        if img is None or axis_entities is None:
            return data
        (img_height, img_width) = img.shape[:2]
        for axis_id, axis_entity in enumerate(axis_entities):
            axis_bbox = axis_entity.get("bbox")
            axis_direction = axis_entity.get("direction")
            axis_score = axis_entity.get("score")
            new_axis_bbox = axis_bbox
            if axis_bbox:
                axis_x = axis_bbox.get("x")
                axis_y = axis_bbox.get("y")
                axis_width = axis_bbox.get("width")
                axis_height = axis_bbox.get("height")
                if axis_x and axis_y and axis_width and axis_height:
                    if axis_x >= 0 and axis_y >= 0 and axis_width > 0 and axis_height > 0:
                        # Step 0: extend the axis image to avoid mistakes
                        if axis_direction == 0:
                            axis_x_extra = max(round(axis_width * 0.02), 6)
                            if axis_x >= axis_x_extra:
                                axis_x = axis_x - axis_x_extra
                                axis_width = axis_width + axis_x_extra
                            if axis_x + axis_width + axis_x_extra < img_width:
                                axis_width = axis_width + axis_x_extra
                        elif axis_direction == 90:
                            axis_y_extra = max(round(axis_height * 0.02), 6)
                            if axis_y >= axis_y_extra:
                                axis_y = axis_y - axis_y_extra
                                axis_height = axis_height + axis_y_extra
                            if axis_y + axis_height + axis_y_extra < img_height:
                                axis_height = axis_height + axis_y_extra
                        new_axis_bbox = {
                            "x": axis_x,
                            "y": axis_y,
                            "width": axis_width,
                            "height": axis_height
                        }
                        # Step 1: crop the axis image
                        axis_img = img[axis_y:(axis_y + axis_height), axis_x:(axis_x + axis_width)].copy()
                        # Step 2: enhance the contrast
                        axis_img_enhanced = contrast_enhance(axis_img)
                        # Step 3: partition the image
                        line_img, tick_img, title_img, ticks_bbox = partition_axis(axis_img_enhanced, \
                            axis_id, axis_direction)
                        tick_texts = None
                        title_texts = None
                        if tick_img is not None and isinstance(tick_img, np.ndarray):
                            tick_img_pil = CV2PIL(tick_img)
                            if TESTING["axis"]["sign"]:
                                tick_img_pil.save(TESTING['dir'] + '/axis_' + str(axis_id) + \
                                '_test_tick.png')
                            tick_texts = pt.image_to_data(tick_img_pil, config='--psm 6')
                            tick_texts = understand_data(tick_texts)
                        if title_img is not None and isinstance(tick_img, np.ndarray):
                            title_img_pil = CV2PIL(title_img)
                            if TESTING["axis"]["sign"]:
                                title_img_pil.save(TESTING['dir'] + '/axis_' + str(axis_id) + \
                                    '_test_title.png')
                            title_texts = pt.image_to_string(title_img_pil, config='--psm 6')
                        if tick_texts is not None:
                            img_shape = {
                                "width": img_width,
                                "height": img_height
                            }
                            formated_axis = get_format_axis(tick_texts, title_texts,\
                                ticks_bbox, img_shape,\
                                new_axis_bbox, axis_direction, axis_score)
                            data.append(formated_axis)
    except Exception as e:
        print(repr(e))
        traceback.print_exc()
    return data
