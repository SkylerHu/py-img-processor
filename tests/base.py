#!/usr/bin/env python
# coding=utf-8
import cv2

import skimage
from skimage.metrics import structural_similarity

from imgprocessor import utils


def compare_imgs_by_path(input_path: str, target_path: str, threshold: int = 1) -> None:
    input_img = cv2.imread(input_path)
    target_img = cv2.imread(target_path)

    assert input_img.shape == target_img.shape, f"{input_img.shape} ==> {target_img.shape}"

    if utils.Version(skimage.__version__) >= utils.Version("0.19"):
        ssim = structural_similarity(input_img, target_img, channel_axis=2)
    else:
        ssim = structural_similarity(input_img, target_img, multichannel=True)

    if utils.get_pil_version != utils.Version("8.4.0"):
        threshold = 0.97

    assert ssim >= threshold, f"ssim {ssim} < {threshold}"
