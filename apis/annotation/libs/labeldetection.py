"""The module for detecting labels"""
import traceback
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from sklearn.cluster import KMeans
from .__settings__ import TESTING
from .image_processing import CV2PIL, contrast_enhance

def get_major_color(colors, colors_rgb):
    """Get the major color of the entity"""
    max_score = float('-inf')
    max_color = None
    max_rgb = None
    if colors and colors_rgb:
        for color in colors:
            c_score = float(colors[color])
            if c_score > max_score:
                max_color = color
                max_score = c_score
                max_rgb = colors_rgb[color]
    return max_rgb

def get_mask_img(img, masks):
    """Get the largest mask of the entity"""
    mask_img = np.zeros(img.shape[:2])
    if masks:
        mask_polygon = np.array([masks], dtype=np.int32)
        cv2.fillPoly(mask_img, mask_polygon, 255)
    return mask_img

def get_label_texts(img, data_entities):
    """The function for detecting labels"""
    if img is None:
        return
    if data_entities:
        for data_id, data_entity in enumerate(data_entities):
            bbox = data_entity.get("bbox")
            mask_img = get_mask_img(img, data_entity.get("mask"))
            colors = data_entity.get("color")
            colors_rgb = data_entity.get("color_rgb")
            major_color_rgb = get_major_color(colors, colors_rgb)
            major_color_bgr = major_color_rgb.reverse()
            if bbox is not None:
                data_x = bbox.get("x")
                data_y = bbox.get("y")
                data_width = bbox.get("width")
                data_height = bbox.get("height")
                if data_x and data_y and data_width and data_height:
                    if data_x >= 0 and data_y >= 0 and data_width > 0 and data_height > 0:
                        data_img = img[data_y:(data_y + data_height),\
                            data_x:(data_x + data_width)].copy()
                        data_mask = mask_img[data_y:(data_y + data_height),\
                            data_x:(data_x + data_width)]
                        # Step 1: fill the other areas with the major color
                        print(np.where(data_mask == 0))
                        print(data_img.shape)
                        data_img[np.where(data_mask == 0)] = major_color_bgr
                        data_img_enhanced = contrast_enhance(data_img)
                        (data_img_h, data_img_w) = data_img.shape[:2]
                        data_img_enhanced = cv2.cvtColor(data_img_enhanced, \
                            cv2.COLOR_BGR2GRAY).astype(np.uint8)
                        data_img_enhanced = cv2.resize(data_img_enhanced, \
                            (2*data_img_w, 2*data_img_h), \
                            interpolation=cv2.INTER_AREA)
                        if TESTING["label"]["sign"]:
                            cv2.imwrite(TESTING['dir'] + '/label_' + str(data_id) + '.png', \
                                data_img_enhanced, \
                                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                        img_pil = CV2PIL(data_img_enhanced)
                        label_texts = pt.image_to_string(img_pil, config='--psm 6')
                        print(label_texts)
