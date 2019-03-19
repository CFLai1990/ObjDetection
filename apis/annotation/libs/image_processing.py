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
