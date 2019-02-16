"""Detect the attributes inside each mask"""
import csv
import numpy as np
import cv2
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000 as color_diff

from .__settings__ import COLOR_CODE, COLOR_DICT

class ObjAttrs:
    """The class for attribute detection"""
    def __init__(self):
        self.init_colors()
        self.color_codes = None

    def init_colors(self):
        """Initialize the 330 Munsell colors"""
        color_list = []
        with open(COLOR_DICT, newline='', encoding='UTF-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')
            for row in reader:
                color = {
                    'color': LabColor(lab_l=row['l'], lab_a=row['a'], lab_b=row['b']),
                    'code': COLOR_CODE.index(row['name'])
                }
                color_list.append(color)
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

    def infer_pixel_color(self, img):
        """Get the color name for each pixel"""
        height = img.shape[0]
        width = img.shape[1]
        print('1')
        codes = np.ones((width, height), dtype=np.int16)
        print(str(width) + ', ' + str(height))
        for row in range(height):
            for col in range(width):
                print('Infer image: ' + row + ', ' + col)
                codes[row][col] = self.infer_color(img[row][col])
        self.color_codes = codes

    def infer(self, img):
        """Get the color names for the whole image"""
        # Turn the image from BGR to LAB
        img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        # Classify the color of each pixel
        self.infer_pixel_color(img_lab)

    def get_mask_color(self, mask_img):
        """Count the colors inside the mask"""
        height = mask_img.shape[0]
        width = mask_img.shape[1]
        code_dict = {}
        for row in range(height):
            for col in range(width):
                if mask_img[row][col] == 255:
                    code = self.color_codes[row][col]
                    if code_dict.get(code) is None:
                        code_dict[code] = 1
                    else:
                        code_dict[code] = code_dict[code] + 1
            pixel_num = float(0)
            for num in code_dict.values():
                pixel_num += num
            color_dict = {}
            for code in code_dict:
                color_name = COLOR_CODE[code]
                color_dict[color_name] = pixel_num / code_dict[code]
        return color_dict

    def clear_all(self):
        """Clear the temporary data"""
        self.color_codes = None

    def get_mask(self, mask_img):
        """Get the colors inside the mask"""
        # mask_img: the binary masked image
        color = self.get_mask_color(mask_img)
        self.clear_all()
        return {
            'color': color,
        }
