#!/usr/bin/env python
# coding=utf-8
import re

from setuptools import setup, find_packages


def read(file_name: str) -> str:
    with open(file_name, "r") as f:
        content = f.read()
    return content


version = re.search("__version__ = ['\"]([^'\"]+)['\"]", read("imgprocessor/__init__.py")).group(1)  # type: ignore

read_me = read("README.md")
# 图片使用 raw 地址以便 PyPI 直接渲染
read_me = read_me.replace(
    "(./docs/imgs/", "(https://raw.githubusercontent.com/skylerhu/py-img-processor/master/docs/imgs/"
)
# 其他相对路径替换为 GitHub blob 页面地址
read_me = read_me.replace("(./", "(https://github.com/skylerhu/py-img-processor/blob/master/")


setup(
    name="py-img-processor",
    version=version,
    url="https://github.com/skylerhu/py-img-processor.git",
    author="SkylerHu",
    author_email="skylerhu@qq.com",
    description="Parameter-driven image processing library built on Pillow.",
    keywords=["image", "img-processor", "image-processor", "imgprocessor", "img-editor", "image-editor"],
    long_description=read_me,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["*tests*", "tests"]),
    license="MIT Licence",
    include_package_data=True,
    zip_safe=False,
    platforms="any",
    entry_points={
        "console_scripts": [
            "img-processor=imgprocessor.main:main",
        ]
    },
    install_requires=[
        "py-enum>=2.1.1",
        "Pillow>=8",
    ],
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
