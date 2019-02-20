"""Detect the attributes inside each mask"""
import time
import os
import csv
import numpy as np
import cv2
from colormath.color_objects import LabColor, HSVColor
from colormath.color_diff import delta_e_cie2000 as color_diff
from colormath.color_conversions import convert_color

from .__settings__ import COLOR_CODE, COLOR_MUNSELL, COLOR_HSV

OUTPUT_DIR = os.path.abspath('./files/annotation')

class ObjAttrs:
    """The class for attribute detection"""
    def __init__(self):
        self.color_list = None
        # self.init_munsell()
        self.init_hsv()
        self.color_codes = None

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
        masked = cv2.bitwise_and(color_codes, color_codes, mask=mask_img)
        unique, counts = np.unique(masked, return_counts=True)
        code_dict = dict(zip(unique, counts))
        pixel_num = float(0)
        for code, num in code_dict.items():
            if code != 0:
                pixel_num += num
        color_dict = {}
        for code in code_dict:
            if code != 0:
                color_name = COLOR_CODE[code]
                color_dict[color_name] = round(code_dict[code] / pixel_num, 4)
        return color_dict

    def get_mask_size(self, contour_list):
        """Get the size of the mask: area, x_range, y_range"""
        area = 0
        areas = []
        ctr_range = {
            'x': [float('inf'), -1],
            'y': [float('inf'), -1]
        }
        for contour in contour_list:
            contour_area = cv2.contourArea(contour)
            areas.append(contour_area)
            area += contour_area
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
        return areas, {
            'area': area,
            'x_range': ctr_range['x'],
            'y_range': ctr_range['y']
        }

    def get_mask_position(self, contour_list, areas, total_area):
        """Get the position of the (centroid of the) mask"""
        ctr_centroid = {
            'x': 0,
            'y': 0,
        }
        print('started')
        for index, contour in enumerate(contour_list):
            contour_area = areas[index]
            ctr = contour.reshape((-1, 2)).astype(float).tolist()
            moment = cv2.moments(contour)
            print('m10: '+ str(moment['m10']))
            print('m01: '+ str(moment['m01']))
            print('m00: '+ str(moment['m00']))
            centroid_x = int(moment['m10']/moment['m00'])
            print('get x')
            centroid_y = int(moment['m01']/moment['m00'])
            print('get y')
            print('x: ' + centroid_x)
            print('y: ' + centroid_x)
            print('area: ' + contour_area)
            ctr_centroid['x'] += contour_area * centroid_x
            ctr_centroid['y'] += contour_area * centroid_y
        print('before')
        ctr_centroid['x'] = int(ctr_centroid['x'] / total_area)
        ctr_centroid['y'] = int(ctr_centroid['y'] / total_area)
        print('after')
        return ctr_centroid

    def clear_all(self):
        """Clear the temporary data"""
        self.color_codes = None

    def get_mask(self, mask_img, contour_list):
        """Get the colors inside the mask"""
        # mask_img: the binary masked image
        color = self.get_mask_color(mask_img)
        areas, size = self.get_mask_size(contour_list)
        print('c')
        position = self.get_mask_position(contour_list, areas, size['area'])
        print('d')
        return {
            'color': color,
            'size': size,
            'position': position
        }
