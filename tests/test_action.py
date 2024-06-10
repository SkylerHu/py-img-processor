#!/usr/bin/env python
# coding=utf-8
import pytest

from imgprocessor.params import ProcessParams
from imgprocessor.processor import process_image_by_path

from .base import compare_imgs_by_path


@pytest.mark.usefixtures("clean_dir")
@pytest.mark.parametrize(
    "img_name,param_str,expected_path",
    [
        ("lenna-400x225.jpg", "resize,s_720", "expected/lenna-400x225.png"),
    ],
)
def test_action(img_name: str, param_str: dict, expected_path: str) -> None:
    # 生成目标文件名称
    target_tag = param_str.replace(",", "-").replace("/", "--")
    target_name, target_type = expected_path.split(".")
    target_path = f"{target_name}-{target_tag}.{target_type}"
    # 图片处理
    params = ProcessParams.parse_str(param_str)
    process_image_by_path(img_name, target_path, params)
    # 比较结果
    compare_imgs_by_path(img_name, target_path)
