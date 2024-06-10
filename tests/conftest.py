#!/usr/bin/env python
# coding=utf-8
import typing

import os
import shutil
import tempfile

import pytest
from PIL import Image

from imgprocessor import enums


def pytest_addoption(parser):
    parser.addoption(
        "--use_special_tmp", action="store_true", default=False, help="临时目录使用.tmp文件夹，不删除，用于肉眼观察图片"
    )


@pytest.fixture()
def use_special_tmp(request: pytest.FixtureRequest) -> typing.Optional[str]:
    return request.config.getoption("--use_special_tmp")


@pytest.fixture
def clean_dir(use_special_tmp: typing.Optional[str]) -> typing.Generator:
    """
    有2个作用：
    - 产生的文件都放在临时目录中，可以在测试用例跑完后删除
    - 将测试图像拷贝一份，避免改动了原测试文件
    """
    old_cwd = os.getcwd()
    img_dir = os.path.join(old_cwd, "tests/imgs")

    if use_special_tmp:
        new_path = os.path.join(old_cwd, ".tmp")
        os.chdir(new_path)
        # 将原始图像复制一份，不然无法在临时目录中按照相对路径访问图片
        shutil.copytree(f"{img_dir}", f"{new_path}", dirs_exist_ok=True)
        yield
        os.chdir(old_cwd)
    else:
        with tempfile.TemporaryDirectory() as new_path:
            os.chdir(new_path)
            # 将原始图像复制一份，不然无法在临时目录中按照相对路径访问图片
            shutil.copytree(img_dir, new_path)
            yield
            os.chdir(old_cwd)


@pytest.fixture
def img_origin() -> Image:
    """原图"""
    im = Image.open("lenna-400x225.jpg")
    return im


@pytest.fixture
def img_rotate_90_with_exif(img_origin: Image) -> Image:
    """逆时针旋转了90度带Orientation方向标识的图，图片展示和原图无异"""
    name = img_origin.filename.split("/")[-1].split(".")[0]
    path = f"{name}_rotate_90_with_exif.jpg"
    exif = img_origin.getexif()
    im = img_origin.convert("RGB")
    im = im.transpose(Image.ROTATE_90)
    exif[0x0112] = enums.ImageOrientation.RIGHT_TOP
    im.save(path, exif=exif)
    im = Image.open(path)
    return im


@pytest.fixture
def img_rotate_90(img_origin: Image) -> Image:
    """逆时针旋转了90度的图"""
    name = img_origin.filename.split("/")[-1].split(".")[0]
    path = f"{name}_rotate_90.jpg"
    im = img_origin.convert("RGB")
    im = im.rotate(90, expand=True)
    im.save(path)
    im = Image.open(path)
    return im
