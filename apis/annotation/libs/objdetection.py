# python2 compatible
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# common packages
from collections import defaultdict
import argparse
import cv2  # NOQA (Must import before importing caffe2 due to bug in cv2)
import glob
import logging
import os
import sys
import time

from caffe2.python import workspace

# The assert_and_infer_cfg function sets all CFG option parameters to read-only to prevent modification
from detectron.core.config import assert_and_infer_cfg
# The CFG option is imported from the config.py file, which contains all the selection parameters of the Detectron model
# Therefore, it is very large (about 1000 lines of code)
from detectron.core.config import cfg
# The merge_cfg_from_file function is used to merge the CFG options in a yaml config file into the global CFG (cfg in core/config.py)
from detectron.core.config import merge_cfg_from_file
from detectron.utils.io import cache_url
from detectron.utils.logging import setup_logging
from detectron.utils.timer import Timer
import detectron.core.test_engine as infer_engine
import detectron.datasets.dummy_datasets as dummy_datasets
import detectron.utils.c2 as c2_utils
from .odvis import vis_one_image

from .__settings__ import DT

c2_utils.import_detectron_ops()

# OpenCL may be enabled by default in OpenCV3; disable it because it's not
# thread safe and causes unwanted GPU memory allocations.
cv2.ocl.setUseOpenCL(False)

class ObjDetection:
  def __init__(self):
    self.dt = DT
    self.logger = logging.getLogger('ObjDetection')
    self.init()

  def init(self):
    # Set up all configurations for Detectron
    merge_cfg_from_file(self.dt['config'])
    cfg.NUM_GPUS = 1
    assert_and_infer_cfg(cache_urls=False)

    # Some protection
    assert not cfg.MODEL.RPN_ONLY, \
      'RPN models are not supported'
    assert not cfg.TEST.PRECOMPUTED_PROPOSALS, \
      'Models that require precomputed proposals are not supported'

    # Initiate the model from configurations
    self.model = infer_engine.initialize_model_from_cfg(self.dt['weights'])
    # Acquire classes from the COCO dataset
    # It returns a AttrDict object stored with 'classes: value'
    # Each value is a dictionary that looks like this: 0:'__background__', 1:'person', ...
    self.classDict = dummy_datasets.get_coco_dataset()

  def infer(self, imgPath, imgType, outputDir):
    print(imgPath)
    print(imgType)
    print(outputDir)
    # get the image name without suffix
    imgName = os.path.basename(imgPath).replace('.' + imgType, '')
    print(imgName)
    # the path of the output file
    outputPath = os.path.join(outputDir, '{}'.format(imgName + '_dt.' + imgType))
    print(outputPath)
    self.logger.info('Processing {} -> {}'.format(imgPath, outputPath))

    # Read the image using opencv, the result is stored in GBR
    img = cv2.imread(imgPath)
    # Start the timer
    timers = defaultdict(Timer)
    t = time.time()
    # Create a GPU name scope and a CUDA device scope.
    with c2_utils.NamedCudaScope(0):
      # Object detection with the configured model
      # Returned: cls_boxes (object detection), cls_segms (instance segmentation), cls_keyps (keypoint detection)
      cls_boxes, cls_segms, cls_keyps = infer_engine.im_detect_all(self.model, img, None, timers=timers)
    self.logger.info('Inference time: {:.3f}s'.format(time.time() - t))
    for k, v in timers.items():
        self.logger.info(' | {}: {:.3f}s'.format(k, v.average_time))

    # Render the masks
    vis_one_image(
        img[:, :, ::-1],  # BGR -> RGB for visualization
        outputPath,
        cls_boxes,
        cls_segms,
        cls_keyps,
        dataset=self.classDict,
        box_alpha=0.3,
        show_class=True,
        thresh=self.dt['threshold_detection'],
        kp_thresh=self.dt['threshold_keypoint'],
        ext=imgType,
        out_when_no_box=True
    )
    return outputPath