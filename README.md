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
| APP_CACHE_REDIS | dict | 用于缓存的redis配置，eg: `{'host': '127.0.0.1', 'port': 6379, 'db': 0, 'socket_timeout': 10}` | None |


### 3.2 日志配置
提供以下几种loggers：
- `pykit_tools` 用于消息的父日志记录器，一般用以下细分的logger
- `pykit_tools.cmd` 用于记录`cmd.exec_command`执行的命令行
- `pykit_tools.error` 用于处理错误时输出，例如`handle_exception`中有用到
