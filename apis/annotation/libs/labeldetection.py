"""The module for detecting labels"""
import traceback
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from sklearn.cluster import KMeans
from .__settings__ import TESTING
from .image_processing import CV2PIL, contrast_enhance

def get_label_texts(img, data_entities):
    """The function for detecting labels"""
    if img is None:
        return
    if data_entities:
        for data_entity in data_entities:
            bbox = data_entity.get("bbox")
            if bbox is not None:
                data_x = bbox.get("x")
                data_y = bbox.get("y")
                data_width = bbox.get("width")
                data_height = bbox.get("height")
                if TESTING["label"]["sign"]:
                    print(bbox)
                    print(data_x, data_y, data_width, data_height)
                if data_x and data_y and data_width and data_height:
                    if data_x >= 0 and data_y >= 0 and data_width > 0 and data_height > 0:
                        data_img = img[data_y:(data_y + data_height), data_x:(data_x + data_width)]
                        data_img_enhanced = contrast_enhance(data_img)
                        (data_img_h, data_img_w) = data_img.shape[:2]
                        data_img_enhanced = cv2.resize(data_img_enhanced, (3*data_img_w, 3*data_img_h), \
                            interpolation=cv2.INTER_AREA)
                        img_pil = CV2PIL(data_img_enhanced)
                        label_texts = pt.image_to_string(img_pil, config='--psm 6')
                        print(label_texts)
