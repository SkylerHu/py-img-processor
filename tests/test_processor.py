#!/usr/bin/env python
# coding=utf-8
import os
import tempfile
import pytest
from PIL import Image

from imgprocessor import settings, enums
from imgprocessor.str_tool import base64url_encode
from imgprocessor.processor import handle_img_actions, save_img_to_file, process_image_by_path
from imgprocessor.parsers import ProcessParams
from imgprocessor.exceptions import ProcessLimitException

from .base import compare_imgs_by_path


def test_handle_actions() -> None:
    params = ProcessParams.parse_str("resize,s_100/crop,w_10,h_10")

    with pytest.raises(ProcessLimitException, match="图像宽和高单边像素不能超过"):
        im = Image.new("L", (settings.PROCESSOR_MAX_PIXEL + 1, 10))
        handle_img_actions(im, params.actions)

    with pytest.raises(ProcessLimitException, match="图像总像素不可超过"):
        im = Image.new("L", (20000, 20000))
        handle_img_actions(im, params.actions)

    im = Image.new("L", (1920, 1080))
    handle_img_actions(im, params.actions)


@pytest.mark.usefixtures("clean_dir")
def test_save_img() -> None:
    im = Image.new("RGBA", (1920, 1080))
    save_img_to_file(im, format=enums.ImageFormat.JPEG, quality=80)
    im.format = enums.ImageFormat.PNG
    save_img_to_file(im)

    im = Image.new("RGB", (1920, 1080))
    im.format = enums.ImageFormat.JPEG
    save_img_to_file(im, format=enums.ImageFormat.JPEG)
    save_img_to_file(im)


@pytest.mark.usefixtures("clean_dir")
def test_by_path() -> None:
    params = ProcessParams.parse_str("resize,s_100/crop,w_10,h_10")
    output_path = "expected/test.jpg"
    process_image_by_path("lenna-400x225.jpg", output_path, params)
    process_image_by_path("lenna-400x225.jpg", output_path, "resize,s_100/crop,w_10,h_10/quality,80")
    process_image_by_path("lenna-400x225.jpg", output_path, {"actions": [{"key": "action", "w": 100}]})

    with pytest.raises(ProcessLimitException, match="图像文件大小不得超过"):
        with tempfile.TemporaryFile() as fp:
            fp.write((settings.PROCESSOR_MAX_FILE_SIZE * 1024 * 1024 + 1) * b"b")
            fp.seek(0)
            process_image_by_path(fp.name, output_path, params)


@pytest.mark.usefixtures("clean_dir")
@pytest.mark.parametrize(
    "img_name,param_str,expected_path",
    [
        # 第一个resize其实没有任何操作
        (
            "lenna-400x225.jpg",
            "resize,s_225/resize,m_fit,w_300,h_200/resize,m_pad,w_100,h_100/rotate,360/alpha,100",
            "expected/lenna-resize-pad.jpg",
        ),
        # 第一个crop其实没有任何操作
        (
            "lenna-400x225.jpg",
            "crop,w_400/resize,s_100/crop,w_100,h_100,g_center/alpha,40/circle,r_100/rotate,45/blur,r_1/format,png",
            "expected/lenna-edit.png",
        ),
        (
            "lenna-400x225.jpg",
            "resize,s_100/crop,w_100,h_100,g_center/gray",
            "expected/lenna-gray.png",
        ),
        (
            "lenna-400x225.jpg",
            f"watermark,image_{base64url_encode('wolf-50.png')},g_center,t_50,rotate_315,"
            f"fill_1,align_1,text_{base64url_encode('Hello 世界')},font_{base64url_encode('PingFang-Heavy.ttf')},size_13",
            "expected/lenna-watermark.jpg",
        ),
        (
            "lenna-400x225.jpg",
            f"watermark,t_100,rotate_360,text_{base64url_encode('Hello 世界')},color_FFFFFF",
            "expected/lenna-watermark-v2.jpg",
        ),
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
