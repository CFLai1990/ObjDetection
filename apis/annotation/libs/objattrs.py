"""Detect the attributes inside each mask"""
import random
import time
import os
import csv
import numpy as np
import cv2
from colormath.color_objects import LabColor, HSVColor
from colormath.color_diff import delta_e_cie2000 as color_diff
from colormath.color_conversions import convert_color
from .image_processing import get_mode, get_major_color
from .__settings__ import COLOR_CODE, COLOR_MUNSELL, COLOR_HSV, TESTING

OUTPUT_DIR = os.path.abspath('./files/annotation')
COLOR_RANGE_HSV = np.array([10, 32, 32], dtype=np.int32)

class ObjAttrs:
    """The class for attribute detection"""
    def __init__(self):
        self.color_list = None
        # self.init_munsell()
        self.init_hsv()
        self.color_codes = None
        self.img = None
        self.img_rgb = None

    def init_munsell(self):
        """Initialize the 330 Munsell colors"""
        color_list = []
        with open(COLOR_MUNSELL, newline='', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                color_lab = LabColor(lab_l=row['l'], lab_a=row['a'], lab_b=row['b'])
                color_hsv = convert_color(color_lab, HSVColor)
                print(color_hsv.get_value_tuple())
                color = {
                    'color': color_lab,
                    #'code': COLOR_CODE.index(row['name'])
                }
                color_list.append(color)
            self.color_list = color_list

    def init_hsv(self):
        """Initialize the hsv color thresholds"""
        color_list = {}
        with open(COLOR_HSV, newline='', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                color_name = row['name']
                if color_list.get(color_name) is None:
                    color_list[color_name] = {
                        'low': [],
                        'high': [],
                        'code': COLOR_CODE.index(row['name'])
                    }
                hsv_threshold = np.array([row['h'], row['s'], row['v']], dtype=np.uint8)
                if str(row['threshold']) == '0':
                    color_list[color_name]['low'].append(hsv_threshold)
                else:
                    color_list[color_name]['high'].append(hsv_threshold)
            self.color_list = color_list

    def infer_color(self, lab):
        """Get the name for one color"""
        color = LabColor(lab_l=lab[0], lab_a=lab[1], lab_b=lab[2])
        min_dist = float('inf')
        code = -1
        for ms_color in self.color_list:
            dist = color_diff(color, ms_color['color'])
            if dist < min_dist:
                code = ms_color['code']
        return code

    def infer_pixel_munsell(self, img):
        """Get the color name for each pixel"""
        height = img.shape[0]
        width = img.shape[1]
        codes = np.ones((height, width), dtype=np.int16)
        print('Infer image started: ' + str(width) + ' * ' + str(height))
        timer = time.time()
        for row in range(height):
            for col in range(width):
                codes[row][col] = self.infer_color(img[row][col])
        print('Infer image ended: {:.3f}s'.format(time.time() - timer))
        self.color_codes = codes

    def infer_pixel_hsv(self, img):
        """Get the color name for each pixel"""
        height = img.shape[0]
        width = img.shape[1]
        codes = np.zeros((height, width), dtype=np.uint8)
        for color in self.color_list.values():
            threshold_num = len(color['low'])
            if threshold_num == 1:
                mask = cv2.inRange(img, color['low'][0], color['high'][0])
            else:
                mask = np.zeros((height, width), dtype=np.uint8)
                for i in range(threshold_num):
                    mask_i = cv2.inRange(img, color['low'][i], color['high'][i])
                    mask = cv2.bitwise_or(mask, mask_i)
            color_map = np.empty((height, width), dtype=np.uint8)
            color_map.fill(color['code'])
            color_map = cv2.bitwise_and(color_map, color_map, mask=mask)
            codes = codes + color_map
        self.color_codes = codes

    def infer(self, img, mode='hsv'):
        """Get the color names for the whole image"""
        self.img = img
        self.img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if mode == 'munsell':
            # Turn the image from BGR to LAB
            img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            # Classify the color of each pixel
            self.infer_pixel_munsell(img_lab)
        else:
            # Turn the image from BGR to HSV
            img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # Classify the color of each pixel
            self.infer_pixel_hsv(img_hsv)

    def get_mask_color(self, mask_img):
        """Count the colors inside the mask"""
        color_codes = self.color_codes
        img = self.img
        img_rgb = self.img_rgb
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        masked = cv2.bitwise_and(color_codes, color_codes, mask=mask_img)
        unique, counts = np.unique(masked, return_counts=True)
        code_dict = dict(zip(unique, counts))
        pixel_num = float(0)
        for code, num in code_dict.items():
            if code != 0:
                pixel_num += num
        color_dict = {}
        rgb_dict = {}
        for code in code_dict:
            if code != 0:
                color_name = COLOR_CODE[code]
                color_dict[color_name] = round(code_dict[code] / pixel_num, 4)
                # The hue of some color inside the mask
                hsv_in_mask = img_hsv[np.where((mask_img > 0) & (color_codes == code))]
                major_color_hsv = np.mean(hsv_in_mask, axis=0).astype(np.uint8)
                fake_img = np.array([[major_color_hsv]], dtype=np.uint8)
                fake_img = cv2.cvtColor(fake_img, cv2.COLOR_HSV2RGB)
                rgb_dict[color_name] = fake_img[0][0]
        return color_dict, rgb_dict

    def get_mask_size(self, contour_list):
        """Get the size of the mask: area, x_range, y_range"""
        total_area = 0
        areas = [] # area of each sub-contour
        invalid_ids = [] # find the invalid sub-contours, store their IDs
        ctr_range = {
            'x': [float('inf'), -1],
            'y': [float('inf'), -1]
        }
        for index, contour in enumerate(contour_list):
            contour_area = cv2.contourArea(contour)
            if contour_area == 0: # Invalid sub-contour: area=0
                invalid_ids.insert(0, index)
                continue
            areas.append(contour_area)
            total_area += contour_area
            left_x, left_y, rect_w, rect_h = cv2.boundingRect(contour)
            right_x = left_x + rect_w
            right_y = left_y + rect_h
            if left_x < ctr_range['x'][0]:
                ctr_range['x'][0] = left_x
            if right_x > ctr_range['x'][1]:
                ctr_range['x'][1] = right_x
            if left_y < ctr_range['y'][0]:
                ctr_range['y'][0] = left_y
            if right_y > ctr_range['y'][1]:
                ctr_range['y'][1] = right_y
        # Remove the invalid sub-contours
        for index in invalid_ids:
            del contour_list[index]
        return areas, {
            'area': total_area,
            'x_range': ctr_range['x'],
            'y_range': ctr_range['y']
        }

    def get_mask_position(self, contour_list, areas, total_area):
        """Get the position of the (centroid of the) mask"""
        ctr_centroid = {
            'x': 0,
            'y': 0,
        }
        for index, contour in enumerate(contour_list):
            contour_area = areas[index]
            moment = cv2.moments(contour)
            centroid_x = int(moment['m10']/moment['m00'])
            centroid_y = int(moment['m01']/moment['m00'])
            ctr_centroid['x'] += contour_area * centroid_x
            ctr_centroid['y'] += contour_area * centroid_y
        ctr_centroid['x'] = int(ctr_centroid['x'] / total_area)
        ctr_centroid['y'] = int(ctr_centroid['y'] / total_area)
        return ctr_centroid

    def clear_all(self):
        """Clear the temporary data"""
        self.color_codes = None
        self.img = None
        self.img_rgb = None

    def get_mask(self, mask_img, contour_list):
        """Get the colors inside the mask"""
        # mask_img: the binary masked image
        color, color_values = self.get_mask_color(mask_img)
        areas, size = self.get_mask_size(contour_list)
        position = self.get_mask_position(contour_list, areas, size['area'])
        return {
            'color': color,
            'color_rgb': color_values,
            'size': size,
            'position': position
        }

    def replace_color(self, img, target_color, bg_color):
        """Replace the target color with the background color"""
        target_code = self.color_list.get(target_color)
        if target_code is None:
            return False
        target_code = int(target_code['code'])
        img[np.where((self.color_codes == target_code))] = bg_color
        return True

    def fix_contours(self, bbox, attributes, contour_list):
        """Fix the contour for pure-color shapes"""
        colors = attributes.get("color")
        colors_rgb = attributes.get("color_rgb")
        if colors is None or colors_rgb is None:
            return contour_list
        img = self.img
        # Set up the mask image
        mask_img = np.zeros(img.shape[:2], dtype=np.uint8)
        bbox_mask = np.zeros(img.shape[:2])
        bbox_poly = np.array([\
            [bbox["x"], bbox["y"]],\
            [bbox["x"] + bbox["width"], bbox["y"]],\
            [bbox["x"] + bbox["width"], bbox["y"] + bbox["height"]],\
            [bbox["x"], bbox["y"] + bbox["height"]],\
            ])
        cv2.fillPoly(bbox_mask, [bbox_poly], 255)
        # Find the contour of the pure-color block
        major_color_hsv = get_major_color(colors, colors_rgb, "hsv")
        major_color_upper = np.array(major_color_hsv, dtype=np.int32) + COLOR_RANGE_HSV
        major_color_lower = np.array(major_color_hsv, dtype=np.int32) - COLOR_RANGE_HSV
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        color_mask = cv2.inRange(img_hsv, major_color_lower, major_color_upper)
        mask_img[np.where((bbox_mask > 0) & (color_mask > 0))] = 255
        rand_id = random.randint(0, 99)
        print(rand_id, major_color_upper, major_color_lower)
        if TESTING["label"]["sign"]:
            cv2.imwrite(TESTING['dir'] + '/mask_' + str(rand_id) + '.png', \
                mask_img, \
                [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
        new_contour_list, hier = cv2.findContours(mask_img, \
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Remove the bad contours
        if new_contour_list:
            bad_contours = []
            for c_id, contour in enumerate(new_contour_list):
                c_length = contour.reshape((-1, 2)).shape[0]
                if c_length <= 2:
                    bad_contours.append(c_id)
            if bad_contours:
                bad_contours.reverse()
                for bad_id in bad_contours:
                    new_contour_list.pop(bad_id)
        return new_contour_list
