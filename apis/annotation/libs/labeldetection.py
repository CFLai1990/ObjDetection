"""The module for detecting labels"""
import traceback
import cv2
import numpy as np
from pytesseract import pytesseract as pt
from sklearn.cluster import KMeans
from .__settings__ import TESTING
from .image_processing import CV2PIL, get_major_color, get_contour_area

GRAY_SCALE_LEVEL = 64
COLOR_RANGE = 16

def get_mask_img(img, masks):
    """Get the largest mask of the entity"""
    mask_img = np.zeros(img.shape[:2])
    major_mask = None
    major_mask_area = float("-inf")
    if masks:
        for mask in masks:
            contour_area = get_contour_area(mask, "list")
            if contour_area > major_mask_area:
                major_mask_area = contour_area
                major_mask = mask
        if major_mask is not None:
            mask_polygon = np.array([[major_mask]], dtype=np.int32)
            cv2.fillPoly(mask_img, mask_polygon, 255)
    if mask_img is not None:
        kernel = np.ones((5, 5), np.uint8)
        mask_img = cv2.erode(mask_img, kernel, iterations=1)
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
            major_color_bgr = get_major_color(colors, colors_rgb, "bgr")
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
                        data_img[np.where(data_mask == 0)] = major_color_bgr
                        # Step 2: smooth the similar colors
                        major_color_upper = np.array(major_color_bgr, dtype=np.int32) + COLOR_RANGE
                        major_color_lower = np.array(major_color_bgr, dtype=np.int32) - COLOR_RANGE
                        color_mask = cv2.inRange(data_img, major_color_lower, major_color_upper)
                        data_img[np.where((data_mask > 0) & (color_mask > 0))] = major_color_bgr
                        (data_img_h, data_img_w) = data_img.shape[:2]
                        data_img = cv2.cvtColor(data_img, \
                            cv2.COLOR_BGR2GRAY).astype(np.uint8)
                        # # Denoising: bilateral filtering
                        # data_img = cv2.bilateralFilter(data_img, 4, 50, 50)
                        # # Simplify the gray scales
                        # data_img = (data_img / GRAY_SCALE_LEVEL).astype(np.uint8)
                        # data_img = data_img * GRAY_SCALE_LEVEL
                        data_img = cv2.resize(data_img, \
                            (2*data_img_w, 2*data_img_h), \
                            interpolation=cv2.INTER_AREA)
                        if TESTING["label"]["sign"]:
                            cv2.imwrite(TESTING['dir'] + '/label_' + str(data_id) + '.png', \
                                data_img, \
                                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
                        img_pil = CV2PIL(data_img)
                        label_texts = pt.image_to_string(img_pil, config='--psm 6')
                        print(label_texts)
