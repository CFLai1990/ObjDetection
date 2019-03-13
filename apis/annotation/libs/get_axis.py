"""The module for detecting axes"""
import math
import csv
import cv2
from PIL import Image, ImageDraw
from pytesseract import pytesseract as pt
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def understand_data(data):
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

def open_image(image_name = "0.png", output_image = "0-out.png"):
    output_name = image_name[:-4] + "_out.png"
    data = pt.image_to_data(Image.open(image_name))
    items = understand_data(data)
    # print(items)
    with open("output.json", "w") as f:
        json.dump(items, f, indent=2)
    draw_image(image_name, output_name, items)

def draw_image(image_name, output_name, items):
    img = Image.open(image_name)
    draw = ImageDraw.Draw(img)
    for item in items:
        draw.rectangle([item["left"], item['top'], item["left"] + item["width"], item["top"] + item["height"]], fill=None, outline="red")
    del draw
    img.save(output_name)

def classify_texts(direction, f_items, ticks, labels):
    """The function for classifying ticks and labels"""
    print("step 0")
    proj_positions = []
    vertical_direction = (direction + 90) / 180 * math.pi
    vec_len = 10
    vertical_vector = {
        "x": vec_len * math.cos(vertical_direction),
        "y": vec_len * math.sin(vertical_direction)
    }
    # Project to the vertical direction
    print("step 1")
    for f_item in f_items:
        pos = f_item.get("position")
        print("item_pos: ", pos)
        print("vec_pos: ", vertical_vector)
        proj_pos = [pos.get("x") * vertical_vector.get("x") + pos.get("y") * vertical_vector.get("y")]
        proj_positions.append(proj_pos)
    proj_data = np.array(proj_positions)
    # Classify based on the projected positions
    print("step 2")
    estimator = KMeans(n_clusters=2)
    estimator.fit(proj_data)
    label_pred = estimator.labels_
    print("labels: ", label_pred)
    classes = {}
    for i in range(len(f_items)):
        label_i = label_pred[i]
        class_i = classes.get(label_i)
        if class_i is None:
            classes[label_i] = [i]
        else:
            class_i.append(i)
    # Assume that there are more ticks texts than the label texts
    print("step 3")
    print("classes: ", classes)
    tick_class = None
    label_class = None
    if len(classes.get(0)) > len(classes.get(1)):
        tick_class = classes.get(0)
        label_class = classes.get(1)
    else:
        tick_class = classes.get(1)
        label_class = classes.get(0)
    # Pack the results
    print("step 4")
    print("tick_class: ", tick_class)
    print("label_class: ", label_class)
    for tick_i in tick_class:
        ticks.append(f_items[tick_i])
        print(ticks)
    for label_i in label_class:
        label = label + f_items[label_i]["text"]
        print(label)
    print("step 5")

def get_format_axis(items, axis_info):
    print('1')
    axis = {}
    axis_direction = axis_info["direction"]
    axis_bbox = {
        "x": axis_info.get("x"),
        "y": axis_info.get("y"),
        "width": axis_info.get("width"),
        "height": axis_info.get("height")
    }
    axis_range = {
        "x": [axis_info.get("x"), axis_info.get("x") + axis_info.get("width")],
        "y": [axis_info.get("y"), axis_info.get("y") + axis_info.get("height")]
    }
    print('2')
    ticks = []
    label = ''
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
            "x": item["left"] + axis_info.get("x"),
            "y": item["top"] + axis_info.get("y"),
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
    print('3')
    # Classify if the texts belong to the ticks or the label
    classify_texts(axis_direction, format_items, ticks, label)
    axis["label"] = label
    axis["axis_data"] = {
        "ticks": ticks,
        "direction": axis_direction
    }
    print('4')
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
    print('5')
    return axis

def get_axis(image_name=None):
    data = []
    image = None
    if image_name:
        image = Image.open(image_name)
    if image:
        img_gray = image.convert("L")
        img = np.asarray(img_gray)

        height = img.shape[0]
        width = img.shape[1]

        line_sum = np.sum(img, axis=1)
        colume_sum = np.sum(img, axis=0)

        x_axis_height = np.argmin(line_sum)
        y_axis_width = np.argmin(colume_sum)

        x_axis_info = {
            "x": 0,
            "y": x_axis_height,
            "width": width,
            "height": height - x_axis_height,
            "direction": 0
        }
        y_axis_info = {
            "x": 0,
            "y": 0,
            "width": width - y_axis_width,
            "height": height,
            "direction": 90
        }
        # Pack the x-axis
        if x_axis_info.get("width") and x_axis_info.get("width") != 0 and x_axis_info.get("height") and x_axis_info.get("height") != 0:
            x_axis = image.crop((x_axis_info["x"], x_axis_info["y"], width - 1, height - 1))
            x_axis_data = pt.image_to_data(x_axis)
            x_items = understand_data(x_axis_data)
            data.append(get_format_axis(x_items, x_axis_info))
        # Pack the y-axis
        if y_axis_info.get("width") and y_axis_info.get("width") != 0 and y_axis_info.get("height") and y_axis_info.get("height") != 0:
            y_axis = image.crop((y_axis_info["x"], y_axis_info["y"], y_axis_width, height - 1))
            y_axis_data = pt.image_to_data(y_axis)
            y_items = understand_data(y_axis_data)
            data.append(get_format_axis(y_items, y_axis_info))
    return data
