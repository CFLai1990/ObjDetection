"""apis.annotation.libs: __settings__"""
import os

# Detectron settings
# MODEL = 'natural'
MODEL = 'vis'

DT_MODEL = {
    'natural': {
        'config': '/home/chufan.lai/packages/Detectron/configs/12_2017_baselines/e2e_mask_rcnn_R-101-FPN_2x.yaml',
        'weights': '/home/chufan.lai/packages/detectron_models/demo/model_final.pkl',
    },
    'vis': {
        'config':'/home/chufan.lai/packages/OD_Images/dtconfigs/e2e_mask_rcnn_R-50-FPN_1x_cls4.yaml',
        'weights': '/home/chufan.lai/packages/detectron_models/test/train_cls4_20190318/cflai_train/generalized_rcnn/model_iter69999.pkl',
    }
}

DT = {
    'config': DT_MODEL[MODEL]['config'],
    'weights': DT_MODEL[MODEL]['weights'],
    'threshold_detection': 0.7,
    'threshold_keypoint': 2.0,
}

# Tessearct settings
TS_LANG = 'eng'

# Testing settings
TESTING = {
    'axis': {
        'sign': False,
    },
    'legend': {
        'sign': False,
    },
    'label': {
        'sign': False,
    },
    'dir': '/home/chufan.lai/testing'
}

FIX_CONTOUR = True

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
