import csv
import cv2
from PIL import Image, ImageDraw
from pytesseract import pytesseract as pt
import json
import numpy as np
import matplotlib.pyplot as plt

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
        # print(f"the head length is {len(head)}")
        # print(f"the attributes length is {len(attributes)}")
        # print(head)
        # print(attributes)
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


# open_image()
# print(items)

def get_format_axis(items, direction, transform_):
    axis = {}
    axis["class"] = "axis"
    axis["score"] = 0.9
    axis["label"] = "value (In Million)"
    min_x = 99999
    min_y = 99999
    max_x = 0
    max_y = 0

    # print(transform_)
    x_trans = transform_[0]
    y_trans = transform_[1]

    ticks = []
    for item in items:
        print(item.get("text"))
        format_item = {}
        format_item["text"] = item["text"].replace("-", "")
        bbox = {}
        bbox["x"] = int(item["left"] + x_trans)
        bbox["y"] = int(item["top"] + y_trans)
        bbox["width"] = item["width"]
        bbox["height"] = item["height"]
        format_item["bbox"] = bbox
        position = {}
        position["x"] = (bbox["x"] + bbox["width"]) / 2
        position["y"] = (bbox["y"] + bbox["height"]) / 2
        format_item["position"] = position
        if format_item["text"] != "":
            ticks.append(format_item)
            if max_x < bbox["x"] + bbox["width"]:
                max_x = bbox["x"] + bbox["width"]
            if max_y < bbox["y"] + bbox["height"]:
                max_y = bbox["y"] + bbox["height"]
            if min_x > bbox["x"]:
                min_x = bbox["x"]
            if min_y > bbox["y"]:
                min_y = bbox["y"]
    axis_data = {}
    axis_data["ticks"] = ticks
    axis_data["direction"] = direction
    axis["axis_data"] = axis_data
    axis["color"] = {"white": 0.8, "black": 0.2}
    axis["bbox"] = {
        "x": min_x,
        "y": min_y,
        "width": max_x - min_x,
        "height": max_y - min_y
    }
    axis["mask"] = [[
        [min_x, min_y],
        [min_x, max_y],
        [max_x, max_y],
        [max_x, min_y]
    ]]
    axis["position"] = {
        "x": (max_x + min_x) / 2,
        "y": (max_y + min_y) / 2
    }
    # print(max_x, min_x, max_y, min_y)
    axis["size"] = {
        "area": (max_y - min_y) * (max_x - min_x),
        "x_range": [min_x, max_x],
        "y_range": [min_y, max_y]
    }

    return axis

def get_axis(image_name=None):
    data = []
    image = None
    if image_name:
        image = Image.open(image_name)
    if image:
        img_gray = image.convert("L")
        img = np.asarray(img_gray)
        # np.sum(img)
        # print(np.sum(img, axis = 1))
        # print(img.shape)

        height = img.shape[0]
        width = img.shape[1]

        line_sum = np.sum(img, axis=1)
        colume_sum = np.sum(img, axis=0)

        x_axis_height = np.argmin(line_sum)
        y_axis_width = np.argmin(colume_sum)

        # print(0, x_axis_height, width, height)
        x_axis = image.crop((0, x_axis_height, width - 1, height - 1))
        y_axis = image.crop((0, 0, y_axis_width, height - 1))
        # print("x axis")
        # print(pt.image_to_string(x_axis))
        x_axis_data = pt.image_to_data(x_axis)
        x_items = understand_data(x_axis_data)
        y_axis_data = pt.image_to_data(y_axis)
        y_items = understand_data(y_axis_data)

        # print(x_items)
        # print(y_items)

        # data["x_axis"] = x_items
        # data["y_axis"] = y_items

        data.append(get_format_axis(x_items, 0, (0, x_axis_height)))
        data.append(get_format_axis(y_items, 90, (0, 0)))
    return data


    # print("\ny axis")
    # print(pt.image_to_string(y_axis))
    # print("total")
    # print(pt.image_to_string(image))


    # if False:
    #     plt.plot(line_sum, [i for i in range(height)])
    # else:
    #     plt.plot( [i for i in range(width)], colume_sum)
    # plt.show()

    # print(img)

def png2whitejpg(image_name = "2.png"):
    image = Image.open(image_name)
    image_numpy = np.asarray(image)


    # img.save("0_gray.jpg")


# png2whitejpg()
# change_2gray("example.png")

# data = get_axis("example.png")
# with open("hahah", "w") as f:
#         json.dump(data, f, indent=2)

# open_image("example.png", 'example_out.png')


# To read the coordinates
# boxes = []
# with open('output.box', 'rb') as f:
#     reader = csv.reader(f, delimiter = ' ')
#     for row in reader:
#         if(len(row)==6):
#             boxes.append(row)

# # Draw the bounding box
# img = cv2.imread('1.png')
# h, w, _ = img.shape
# for b in boxes:
#     img = cv2.rectangle(img,(int(b[1]),h-int(b[2])),(int(b[3]),h-int(b[4])),(255,0,0),2)

# cv2.imshow('output',img)
