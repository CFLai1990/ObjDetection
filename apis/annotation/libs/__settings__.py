"""apis.annotation.libs: __settings__"""
import os

# MODEL = 'natural'
MODEL = 'vis'

DT_MODEL = {
    'natural': {
        'config': '/home/chufan.lai/packages/Detectron/configs/12_2017_baselines/e2e_mask_rcnn_R-101-FPN_2x.yaml',
        'weights': '/home/chufan.lai/packages/detectron_models/demo/model_final.pkl',
    },
    'vis': {
        'config':'/home/chufan.lai/packages/Detectron/configs/test_config.yaml',
        'weights': '/tmp/detectron-output/train/coco_2014_train/generalized_rcnn/model_final.pkl',
        # 'weights': '/export3/users/can.liu/annotation/model/20190312/train/coco_2014_train/generalized_rcnn/model_iter94999.pkl',
    }
}

#Detectron settings
DT = {
    'config': DT_MODEL[MODEL]['config'],
    'weights': DT_MODEL[MODEL]['weights'],
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
