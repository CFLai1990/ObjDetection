"""Object Detection"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# common packages
from collections import defaultdict
import os
import time
import logging
import cv2    # NOQA (Must import before importing caffe2 due to bug in cv2)

# The assert_and_infer_cfg function sets all CFG option parameters
# to read-only to prevent modification
from detectron.core.config import assert_and_infer_cfg
# The CFG option is imported from the config.py file, which contains
# all the selection parameters of the Detectron model
# Therefore, it is very large (about 1000 lines of code)
from detectron.core.config import cfg
# The merge_cfg_from_file function is used to merge the CFG options
# in a yaml config file into the global CFG (cfg in core/config.py)
from detectron.core.config import merge_cfg_from_file
# from detectron.utils.io import cache_url
# from detectron.utils.logging import setup_logging
from detectron.utils.timer import Timer
import detectron.core.test_engine as infer_engine
import detectron.datasets.dummy_datasets as dummy_datasets
import detectron.utils.c2 as c2_utils
from .vis_dataset import get_vis_dict
from .odvis import vis_one_image, parse_results
from .objattrs import ObjAttrs

from .__settings__ import MODEL, DT

c2_utils.import_detectron_ops()

# OpenCL may be enabled by default in OpenCV3; disable it because it's not
# thread safe and causes unwanted GPU memory allocations.
cv2.ocl.setUseOpenCL(False)

class ObjDetection:
    """Object Detection Class"""
    def __init__(self):
        self.setting = DT
        self.logger = logging.getLogger('ObjDetection')
        self.result = None
        self.init()

    def init(self):
        """Set up all configurations for Detectron"""
        merge_cfg_from_file(self.setting['config'])
        cfg.NUM_GPUS = 1
        assert_and_infer_cfg(cache_urls=False)

        # Some protection
        assert not cfg.MODEL.RPN_ONLY, \
            'RPN models are not supported'
        assert not cfg.TEST.PRECOMPUTED_PROPOSALS, \
            'Models that require precomputed proposals are not supported'

        # Initiate the model from configurations
        self.model = infer_engine.initialize_model_from_cfg(self.setting['weights'])
        # Acquire classes from the COCO dataset
        # It returns a AttrDict object stored with 'classes: value'
        # Each value is a dictionary that looks like this: 0:'__background__', 1:'person', ...
        if MODEL == "natural":
            self.class_dict = dummy_datasets.get_coco_dataset()
        elif MODEL == "vis":
            self.class_dict = get_vis_dict()
        self.obj_attrs = ObjAttrs()

    def infer(self, img_path):
        """Execute object detection for the image"""
        # Read the image using opencv, the result is stored in GBR
        img = cv2.imread(img_path)
        # Start the timer
        timers = defaultdict(Timer)
        timer = time.time()
        # Create a GPU name scope and a CUDA device scope.
        with c2_utils.NamedCudaScope(0):
            # Object detection with the configured model
            # Returned: cls_boxes (object detection), cls_segms (instance segmentation),
            # cls_keyps (keypoint detection)
            cls_boxes, cls_segms, cls_keyps = infer_engine.im_detect_all(
                self.model, img, None, timers=timers)
        self.logger.info('Inference time: {:.3f}s'.format(time.time() - timer))
        for key, value in timers.items():
            self.logger.info(' | {}: {:.3f}s'.format(key, value.average_time))
        self.result = {
            'boxes': cls_boxes,
            'segms': cls_segms,
            'keyps': cls_keyps
        }
        return img

    def infer_image(self, img_path, img_type, ouput_dir):
        """Infer and return the masked image"""
        # get the image name without suffix
        img_name = os.path.basename(img_path).replace('.' + img_type, '')
        # the path of the output file
        output_path = os.path.join(ouput_dir, '{}'.format(img_name + '_dt.png'))
        self.logger.info('Processing %s -> %s', img_path, output_path)
        # Run object detection
        img = self.infer(img_path)
        # Render the masks
        vis_one_image(
            img[:, :, ::-1],    # BGR -> RGB for visualization
            output_path,
            self.result['boxes'],
            self.result['segms'],
            self.result['keyps'],
            dataset=self.class_dict,
            box_alpha=0.3,
            show_class=True,
            thresh=self.setting['threshold_detection'],
            kp_thresh=self.setting['threshold_keypoint'],
            out_when_no_box=True
        )
        return output_path

    def infer_parameters(self, img_path):
        """Infer and return the mask parameters"""
        self.logger.info('Processing %s -> parameters', img_path)
        # Run object detection
        img = self.infer(img_path)
        # Get the result parameters
        parameters, contours = parse_results(
            self.result['boxes'],
            self.result['segms'],
            self.result['keyps'],
            image=img,
            attrs=self.obj_attrs,
            dataset=self.class_dict,
            thresh=self.setting['threshold_detection'],
            out_when_no_box=True
        )
        return parameters

    def infer_image_with_parameters(self, img_path, img_type, ouput_dir):
        """Infer and return both the masked image and the parameters"""
        # get the image name without suffix
        img_name = os.path.basename(img_path).replace('.' + img_type, '')
        # the path of the output file
        output_path = os.path.join(ouput_dir, '{}'.format(img_name + '_dt.png'))
        self.logger.info('Processing %s -> %s', img_path, output_path)
        # Run object detection
        img = self.infer(img_path)
        # Render the masks
        parameters, contours = parse_results(
            self.result['boxes'],
            self.result['segms'],
            self.result['keyps'],
            image=img,
            attrs=self.obj_attrs,
            dataset=self.class_dict,
            thresh=self.setting['threshold_detection'],
            out_when_no_box=True
        )
        vis_one_image(
            img[:, :, ::-1],    # BGR -> RGB for visualization
            output_path,
            self.result['boxes'],
            self.result['segms'],
            self.result['keyps'],
            dataset=self.class_dict,
            box_alpha=0.3,
            show_class=True,
            thresh=self.setting['threshold_detection'],
            kp_thresh=self.setting['threshold_keypoint'],
            out_when_no_box=True,
            contours_dict=contours
        )
        return output_path, parameters
        