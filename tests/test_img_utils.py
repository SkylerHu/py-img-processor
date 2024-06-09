#!/usr/bin/env python
# coding=utf-8
import os

import pytest

from PIL import Image

from imgprocessor import enums


@pytest.fixture
def img_origin(origin_img_name: str) -> Image:
    """原图"""
    cur_dir = os.getcwd()
    path = os.path.join(cur_dir, origin_img_name)
    im = Image.open(path)
    return im


@pytest.fixture
def img_rotate_90(img_origin: Image) -> Image:
    path = os.path.join(os.getcwd(), "img_rotate_90.jpg")
    exif = img_origin.getexif()
    im = img_origin.convert("RGB")
    im = im.transpose(Image.ROTATE_90)
    exif[0x0112] = enums.ImageOrientation.RIGHT_TOP
    im.save(path, exif=exif)

    im = Image.open(path)
    return im


@pytest.mark.usefixtures("clean_dir")
def test_file(img_origin: Image, img_rotate_90: Image) -> None:
    assert img_origin is None, img_origin.mode
