"""The module for image processing functions"""
from PIL import Image
import numpy as np
import cv2

def PIL2CV(img_PIL):
    """Convert a PIL image to a CV2 image"""
    return cv2.cvtColor(np.asarray(img_PIL), cv2.COLOR_RGB2BGR)

def CV2PIL(img_CV):
    """Convert a CV2 image to a PIL image"""
    return Image.fromarray(cv2.cvtColor(img_CV, cv2.COLOR_BGR2RGB))

def contrast_enhance(axis_img):
    """Enhance the contrast of the axis image"""
    lab= cv2.cvtColor(axis_img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img

def get_mode(array):
    """Find the mode in the array"""
    mode = None
    if isinstance(array, np.ndarray):
        counter = np.bincount(array.flatten())
        mode = int(np.argmax(counter))
    return mode
    