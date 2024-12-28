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

依赖：

- `Python >= 3.9`
- `Pillow >= 8.0.0`

可查看版本变更记录 [ChangeLog](./docs/CHANGELOG-1.x.md)

## 2. 使用(Usage)

具体使用说明查看 [readthedocs](https://py-img-processor.readthedocs.io/) 。

## 2.1 运行配置
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
| PROCESSOR_WORKSPACES | tuple | 限制水印等资源路径 （startswith匹配）， 默认无限制 | `()` |
| PROCESSOR_ALLOW_DOMAINS | tuple | 限制链接地址域名 （endswith匹配），默认无限制 | `()` |

> `注意`：`PROCESSOR_TEXT_FONT` 字体的设置是文字水印必要参数，需保证系统已安装该字体。默认值 `Arial Unicode.ttf` 是MacOS系统存在的字体，建议设置字体文件路径。

## 2.2 图像处理

测试图片 `lenna-400x225.jpg` (像素400x225)

![](./docs/imgs/lenna-400x225.jpg)


### 处理函数
```python
from imgprocessor.processor import process_image

process_image(input_uri, out_path, params)
```

参数说明：

- `input_uri` str，输入图像文件路径或者链接地址
- `out_path` str, 输出图像保存路径
- `params` str or json，图像处理参数，参数说明详见 [Reference.md](./docs/Reference.md)


### 图像处理参数为字符串

- 斜线 `/` 隔开，区分不同的操作；
- 逗号 `,` 隔开，区分操作中不同的参数；
- 下划线 `_` 隔开，`key_value` 的形式，区分参数的Key和Value；
- `value`是复杂参数时，需要进行`base64url_encode`，是否需要encode查看文档参数详细说明；

```python
from imgprocessor.utils import base64url_encode
from imgprocessor.processor import process_image

process_image(
    "docs/imgs/lenna-400x225.jpg",
    "/tmp/output.png",
    # 对图片缩放、裁剪、生成圆角、并转成png存储
    f"resize,s_200/crop,w_200,h_200,g_center/watermark,text_{base64url_encode('Hello 世界')},color_FFF,size_20/circle,r_10/format,png",
)
```

输出图像 (像素200x200)：

![](./docs/imgs/lenna-edit.png)

### 图像处理参数为JSON
- 只是形式不同，参数和字符串形式无本质区别；
- `format`、`quality`、`interlace`三个值在JSON第一层，直接按照`key: value`的形式设置；
- 其他参数都放在 `actions` 数组中；

```python
process_image(
    "docs/imgs/lenna-400x225.jpg",
    "/tmp/output.png",
    {
        "actions": [
            {"key": "resize", "s": 200},
            {"key": "crop", "w": 200, "h": 200, "g": "center"},
            # JSON形式参数, text无需encode
            {"key": "watermark", "text": "Hello 世界", "color": "FFF", "size": 20},
            {"key": "circle", "r": 10},
        ],
        "format": "png",
    },
)
```
该操作与上述字符串示例参数等效。

## 命令行
安装库后 有可执行命令 `img-processor` 可以使用，通过 `img-processor -h` 查看参数说明。

```shell
usage: img-processor [-h] [-V] -P PATH [--action ACTION [ACTION ...]] -O OUTPUT [--overwrite]

图像处理

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -P PATH, --path PATH  输入图像的文件路径/目录，若是目录则批量处理目录下所有图像
  --action ACTION [ACTION ...]
                        操作参数，可对同一个文件多组操作
  -O OUTPUT, --output OUTPUT
                        输出图像路径，多个图像或多个操作时请设置已存在的目录
  --overwrite           是否覆盖输出路径中已有文件
```

示例：
```shell
# 对单个图像进行多个操作，actions有2个参数，会输出2个图像文件
img-processor -P docs/imgs/lenna-400x225.jpg -O /tmp/ --action resize,s_200/format,webp resize,s_225/crop,w_225,h_225,g_center/circle/format,png --overwrite
```

> 注意：action参数仅支持字符串表达形式。

会输出2个图像文件：

`/tmp/lenna-400x225-0.webp` (像素355x200)

![](./docs/imgs/lenna-400x225-0.webp)

`/tmp/lenna-400x225-1.png` (像素225x225)

![](./docs/imgs/lenna-400x225-1.png)


## 提取图像主色调
```python
from imgprocessor.processor import extract_main_color

extract_main_color("docs/imgs/lenna-400x225.jpg")
# 输出： "905C4C"
```
