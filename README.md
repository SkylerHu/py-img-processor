# py-img-processor

[![PyPI - Version](https://img.shields.io/pypi/v/py-img-processor)](https://github.com/SkylerHu/py-img-processor)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/py-img-processor/actions/workflows/pre-commit.yml/badge.svg?branch=master)](https://github.com/SkylerHu/py-img-processor)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/py-img-processor/actions/workflows/test-py3.yml/badge.svg?branch=master)](https://github.com/SkylerHu/py-img-processor)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/SkylerHu/py-img-processor?branch=master)](https://github.com/SkylerHu/py-img-processor)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/py-img-processor)](https://github.com/SkylerHu/py-img-processor)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-img-processor)](https://github.com/SkylerHu/py-img-processor)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/py-img-processor)](https://github.com/SkylerHu/py-img-processor)
[![GitHub License](https://img.shields.io/github/license/SkylerHu/py-img-processor)](https://github.com/SkylerHu/py-img-processor)


Image editor using Python and Pillow.

依赖Pillow开发的Python库，用于图像编辑处理。

## 1. 安装

	pip install py-img-processor

可查看版本变更记录 [ChangeLog](docs/CHANGELOG-1.x.md)

## 2. 使用(Usage)

## 3. 配置

### 3.1 运行配置
可以通过指定环境变量`PY_SETTINGS_MODULE`加载配置文件：

    export PY_SETTINGS_MODULE=${your_project.settings_file.py}

支持的配置项有：

| 配置项 | 类型 | 说明 | 默认值 |
| - | - | - | - |
| DEBUG | bool | 是否debug开发模式 | False |
| PROCESSOR_MAX_FILE_SIZE | int | 处理原图的大小限制， 单位 MB | 20 |
| PROCESSOR_MAX_W_H | int | 处理图像，原图宽高像素限制 | 30000 |
| PROCESSOR_MAX_PIXEL | int | width x height总像素3亿，处理前后的值都被此配置限制 | 300000000 |
| PROCESSOR_DEFAULT_QUALITY | int | 图像处理后的默认质量 | 75 |
| PROCESSOR_TEXT_FONT | str | 默认字体文件，默认从系统中寻找；也可以直接传递字体文件路径 | Arial Unicode.ttf |
