#!/usr/bin/env python
# coding=utf-8
import typing

import os
import shutil
import tempfile

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--use_special_tmp", action="store_true", default=False, help="临时目录使用.tmp文件夹，不删除，用于肉眼观察图片"
    )


@pytest.fixture()
def use_special_tmp(request: pytest.FixtureRequest) -> typing.Optional[str]:
    return request.config.getoption("--use_special_tmp")


@pytest.fixture()
def origin_img_name() -> str:
    return "origin.jpg"


@pytest.fixture
def clean_dir(origin_img_name: str, use_special_tmp: typing.Optional[str]) -> typing.Generator:
    """
    有2个作用：
    - 产生的文件都放在临时目录中，可以在测试用例跑完后删除
    - 将测试图像拷贝一份，避免改动了原测试文件
    """
    old_cwd = os.getcwd()
    ori_path = os.path.join(old_cwd, "docs/imgs/geographical.jpg")

    if use_special_tmp:
        new_path = os.path.join(old_cwd, ".tmp")
        os.chdir(new_path)
        # 将原始图像复制一份，避免意外改动了
        path = os.path.join(new_path, origin_img_name)
        shutil.copyfile(ori_path, path)
        yield
        os.chdir(old_cwd)
    else:
        with tempfile.TemporaryDirectory() as new_path:
            os.chdir(new_path)
            # 将原始图像复制一份，避免意外改动了
            path = os.path.join(new_path, origin_img_name)
            shutil.copyfile(ori_path, path)
            yield
            os.chdir(old_cwd)
