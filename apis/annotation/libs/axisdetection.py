"""The module for detecting axes"""
import math
from PIL import Image
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from sklearn.cluster import KMeans
from .__settings__ import TS_LANG

def PIL2CV(img_PIL):
    """Convert a PIL image to a CV2 image"""
    return cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)

def CV2PIL(img_CV):
    """Convert a CV2 image to a PIL image"""
    return Image.fromarray(cv2.cvtColor(img_CV, cv2.COLOR_BGR2RGB))

def understand_data(data):
    """Parse the pytesseract data"""
    lines = data.split("\n")
    items = []
    # print(lines)
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

def get_axis_partial(axis_img_gray, axis_id):
    """Partition the axis image into three parts: line, tick_texts and title"""
    line_img = None
    tick_text_img = None
    title_img = None
    axis_array = np.array(axis_img_gray, dtype=np.uint8)
    # np.savetxt('/home/chufan.lai/axis_' + str(axis_id) + '.txt', axis_array)
    axis_img_gray.save('/home/chufan.lai/axis_' + str(axis_id) + '.png')
    return line_img, tick_text_img, title_img

def contrast_enhance(axis_img_PIL):
    """Enhance the contrast of the axis image"""
    img = PIL2CV(axis_img_PIL)
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    final_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return CV2PIL(final_img)

def get_axes_texts(img_path, axis_entities):
    """The function for getting the texts in the axis"""
    data = []
    image = None
    # No axes in the image
    if not axis_entities:
        return data
    # Parse the texts of the axes
    if img_path:
        image = Image.open(img_path)
    if image:
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
                        axis_img = image.crop((axis_x, axis_y, axis_x + axis_width, axis_y + axis_height))
                        # Step 2: enhance the contrast
                        axis_img_gray = contrast_enhance(axis_img).convert("L")
                        # Step 3: partition the image
                        line_img, tick_text_img, title_img = get_axis_partial(axis_img_gray, axis_id)
                        # line_sum = np.sum(axis_img_gray, axis=1) / axis_img_gray.shape[1]
                        # column_sum = np.sum(axis_img_gray, axis=0) / axis_img_gray.shape[0]
                        axis_texts = pt.image_to_data(axis_img_gray, lang=TS_LANG)
                        axis_texts = understand_data(axis_texts)
                        formated_axis = get_format_axis(axis_texts, axis_bbox, axis_direction)
                        data.append(formated_axis)
                        axis_id = axis_id + 1
    return data
