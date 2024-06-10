#!/usr/bin/env python
# coding=utf-8
import cv2
from skimage.metrics import structural_similarity


def compare_imgs_by_path(input_path: str, target_path: str, threshold: int = 1) -> None:
    input_img = cv2.imread(input_path)
    target_img = cv2.imread(target_path)

    assert input_img.shape == target_img.shape

    ssim = structural_similarity(input_img, target_img, multichannel=True)

    assert ssim >= threshold, f"ssim {ssim} < {threshold}"
