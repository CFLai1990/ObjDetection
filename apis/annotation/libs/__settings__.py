"""apis.annotation.libs: __settings__"""
import os

#Detectron settings
DT = {
    'config': '/home/chufan.lai/packages/Detectron/configs/12_2017_baselines/e2e_mask_rcnn_R-101-FPN_2x.yaml',
    'weights': '/home/chufan.lai/packages/detectron_models/demo/model_final.pkl',
    # 'weights': '/tmp/detectron-output/train/coco_2014_train/generalized_rcnn/model_final.pkl',
    'threshold_detection': 0.7,
    'threshold_keypoint': 2.0,
}

COLOR_MUNSELL = os.path.abspath('./apis/annotation/data/color_name.csv')
COLOR_HSV = os.path.abspath('./apis/annotation/data/color_threshold.csv')
COLOR_CODE = [
    'others',
    'black',
    'gray',
    'white',
    'red',
    'brown',
    'orange',
    'yellow',
    'green',
    'blue',
    'purple',
    'pink',
]
