#!/usr/bin/env python
# coding=utf-8
import pytest
import os

from imgprocessor.processor import process_image_by_path

from .base import compare_imgs_by_path


@pytest.mark.usefixtures("clean_dir")
@pytest.mark.parametrize(
    "img_name,param_str,expected_path",
    [
        ("lenna-400x225.jpg", "resize,s_200", "expected/lenna-400x225-resize-s_200.jpg"),
    ],
)
def test_action(img_name: str, param_str: dict, expected_path: str) -> None:
    # 生成目标文件名称
    target_path = f"output/{os.path.basename(expected_path)}"
    target_dir = os.path.dirname(target_path)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    # 图像处理
    process_image_by_path(img_name, target_path, param_str)
    # 比较结果
    compare_imgs_by_path(target_path, expected_path)
