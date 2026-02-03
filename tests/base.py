#!/usr/bin/env python
# coding=utf-8
import cv2
import hashlib

from PIL import Image

import skimage
from skimage.metrics import structural_similarity

from imgprocessor import utils


def get_md5(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def compare_imgs_by_path(input_path: str, target_path: str, threshold: int = 1) -> None:
    im_input = Image.open(input_path)
    if getattr(im_input, "is_animated", False):
        # 动图
        if utils.get_pil_version == utils.Version("8.4.0"):
            # 指定版本对比md5
            input_md5 = get_md5(input_path)
            target_md5 = get_md5(target_path)
            assert input_md5 == target_md5
        else:
            # 判断格式是否一致
            im_target = Image.open(target_path)
            assert im_input.format == im_target.format
            assert im_input.mode == im_target.mode
        return

    input_img = cv2.imread(input_path)
    target_img = cv2.imread(target_path)

    assert input_img.shape is not None
    assert target_img.shape is not None
    assert input_img.shape == target_img.shape, f"{input_img.shape} ==> {target_img.shape}"

    if utils.Version(skimage.__version__) >= utils.Version("0.19"):
        ssim = structural_similarity(input_img, target_img, channel_axis=2)
    else:
        ssim = structural_similarity(input_img, target_img, multichannel=True)

    if utils.get_pil_version != utils.Version("8.4.0"):
        threshold = 0.96

    assert ssim >= threshold, f"ssim {ssim} < {threshold}"
