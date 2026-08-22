# py-img-processor

**中文文档** | [English](./README.md)

[![PyPI - Version](https://img.shields.io/pypi/v/py-img-processor)](https://pypi.org/project/py-img-processor/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/py-img-processor)](https://pypistats.org/packages/py-img-processor)
[![GitHub Actions Workflow Status](https://github.com/skylerhu/py-img-processor/actions/workflows/pre-commit.yml/badge.svg?branch=master)](https://github.com/skylerhu/py-img-processor)
[![GitHub Actions Workflow Status](https://github.com/skylerhu/py-img-processor/actions/workflows/test-py3.yml/badge.svg?branch=master)](https://github.com/skylerhu/py-img-processor)
[![Codecov](https://codecov.io/gh/skylerhu/py-img-processor/graph/badge.svg?token=ELSP6KWXDQ)](https://codecov.io/gh/skylerhu/py-img-processor)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/py-img-processor)](https://pypi.org/project/py-img-processor/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-img-processor)](https://pypi.org/project/py-img-processor/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/py-img-processor)](https://pypi.org/project/py-img-processor/)
[![GitHub License](https://img.shields.io/github/license/skylerhu/py-img-processor)](https://github.com/skylerhu/py-img-processor/blob/master/LICENSE)
[![Read the Docs](https://img.shields.io/readthedocs/py-img-processor)](https://py-img-processor.readthedocs.io/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**用一行字符串参数或一段 JSON 驱动整条图像处理流水线。**

py-img-processor 是一个基于 [Pillow](https://python-pillow.org/) 的参数配置化图像处理库，面向后端服务和自动化脚本场景。通过字符串或 JSON 描述处理步骤，即可完成缩放、裁剪、水印、拼接等常见图像操作——同时提供 Python API 和 `img-processor` 命令行工具。

---

## 功能特性

- **缩放** — 等比 / 固定 / 填充 / 裁切等多种缩放模式
- **裁剪** — 坐标、比例、九宫格定位
- **圆角** — 任意半径，支持圆形裁切
- **模糊** — 高斯模糊
- **旋转** — 0–360 度任意角度
- **透明度 / 灰度图**
- **水印** — 文字水印 & 图片水印，支持平铺、旋转、透明度
- **图像合并 / 拼接** — 支持前景 / 背景叠加
- **格式转换** — JPEG / PNG / WebP，可选渐进显示与质量控制
- **主色提取** — 获取图像主色调（HEX）
- **CLI** — 安装即用的 `img-processor` 命令行工具，支持批量处理

---

## 环境要求

- Python >= 3.9
- Pillow >= 8.0.0

## 安装

```bash
pip install py-img-processor
```

> HEIF / AVIF 等扩展格式支持见下方 [扩展格式](#扩展格式支持) 章节。

---

## 快速开始

### Python 接口

```python
from imgprocessor.processor import process_image

# 缩放 → 裁剪 → 文字水印 → 圆角 → 转 PNG，一行搞定
process_image(
    "photo.jpg",
    "resize,s_200/crop,w_200,h_200,g_center/watermark,text_SGVsbG8,color_FFF,size_20/circle,r_10/format,png",
    out_path="output.png",
)
```

输入 `photo.jpg`（400x225）：

![](./docs/imgs/lenna-400x225.jpg)

输出 `output.png`（200x200）：

![](./docs/imgs/lenna-edit.png)

> `text_SGVsbG8` 中的值需要 Base64 URL 编码，可使用内置工具函数：
>
> ```python
> from imgprocessor.utils import base64url_encode
> base64url_encode("Hello 世界")  # => "SGVsbG8g5LiW55WM"
> ```

### JSON 参数（等效写法）

当参数较复杂时，推荐使用 JSON 格式——可读性更好，且 `text` 等字段**无需 Base64 编码**。

```python
process_image(
    "photo.jpg",
    {
        "actions": [
            {"key": "resize", "s": 200},
            {"key": "crop", "w": 200, "h": 200, "g": "center"},
            {"key": "watermark", "text": "Hello 世界", "color": "FFF", "size": 20},
            {"key": "circle", "r": 10},
        ],
        "format": "png",
    },
    out_path="output.png",
)
```

### 直接处理 Image 对象

如果你已经有一个 Pillow `Image` 对象，可以直接传入：

```python
from PIL import Image
from imgprocessor.processor import process_image_obj

with Image.open("photo.jpg") as im:
    process_image_obj(im, "resize,s_200/format,webp", out_path="output.webp")
```

### 提取主色调

```python
from imgprocessor.processor import extract_main_color

extract_main_color("photo.jpg")  # => "905C4C"
```

![#905C4C](https://img.shields.io/static/v1?label=&message=%23905C4C&color=905C4C&style=flat-square)

---

## 命令行工具

安装后即可使用 `img-processor` 命令：

```
img-processor -P <输入路径> --action <操作参数> -O <输出路径> [--overwrite]
```

| 参数 | 说明 |
| --- | --- |
| `-P`, `--path` | 输入图像文件路径或目录（目录时批量处理） |
| `--action` | 操作参数（字符串形式），可传多组 |
| `-O`, `--output` | 输出路径（多图或多操作时请指定已存在的目录） |
| `--overwrite` | 允许覆盖已有文件 |
| `-V`, `--version` | 显示版本号 |

**示例：对单张图片执行两组操作，输出两个文件**

```bash
img-processor \
  -P docs/imgs/lenna-400x225.jpg \
  -O /tmp/ \
  --action \
    "resize,s_200/format,webp" \
    "resize,s_225/crop,w_225,h_225,g_center/circle/format,png" \
  --overwrite
```

输出：

`/tmp/lenna-400x225-0.webp`（355x200）

![](./docs/imgs/lenna-400x225-0.webp)

`/tmp/lenna-400x225-1.png`（225x225）

![](./docs/imgs/lenna-400x225-1.png)

---

## 参数语法

### 字符串格式

```
操作1,参数1_值1,参数2_值2/操作2,参数1_值1
```

| 分隔符 | 作用 |
| --- | --- |
| `/` | 分隔不同操作 |
| `,` | 分隔同一操作内的参数 |
| `_` | 分隔参数的 key 和 value |

> 当 value 是复杂内容（如中文文本、文件路径）时，需要使用 `base64url_encode` 编码。

### JSON 格式

- `format`、`quality`、`interlace`、`animation` 放在 JSON 顶层
- 其余操作放在 `actions` 数组中，每个操作是一个含 `key` 字段的字典

完整参数文档见 [图像处理参数](./docs/Reference.zh.md) 或 [在线文档](https://py-img-processor.readthedocs.io/)。

---

## 配置

通过环境变量 `PY_SETTINGS_MODULE` 指定配置文件（也兼容 `DJANGO_SETTINGS_MODULE`）：

```bash
export PY_SETTINGS_MODULE=your_project.settings
```

| 配置项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `DEBUG` | bool | `False` | 调试模式 |
| `PROCESSOR_MAX_FILE_SIZE` | int | `20` | 原图大小上限（MB） |
| `PROCESSOR_MAX_W_H` | int | `30000` | 单边像素上限 |
| `PROCESSOR_MAX_PIXEL` | int | `300000000` | 总像素上限（宽 x 高），同时覆盖 Pillow 的 `MAX_IMAGE_PIXELS` |
| `PROCESSOR_DEFAULT_QUALITY` | int | `75` | 输出默认质量 |
| `PROCESSOR_TEXT_FONT` | str | `Arial Unicode.ttf` | 文字水印字体，建议设为字体文件绝对路径 |
| `PROCESSOR_WORKSPACES` | tuple | `()` | 限制水印等资源可访问的目录（`startswith` 匹配） |
| `PROCESSOR_ALLOW_DOMAINS` | tuple | `()` | 限制 URL 资源的域名白名单（`endswith` 匹配） |
| `PROCESSOR_TEMP_DIR` | str | `None` | 临时文件目录，未设置则使用系统默认 |

> **注意**: `PROCESSOR_TEXT_FONT` 是文字水印的必要前提——请确保系统已安装该字体，或直接设置为字体文件路径。默认值 `Arial Unicode.ttf` 仅在 macOS 可用。

---

## <a id="扩展格式支持"></a>扩展格式支持

本库基于 Pillow，默认支持 JPEG、PNG、WebP。如需处理 HEIF（`.heic`）或 AVIF（`.avif`），可通过插件扩展：

| 格式 | 方案 |
| --- | --- |
| AVIF | Pillow >= 12.0.0 已内置支持；低版本可安装 [pillow-avif-plugin](https://pypi.org/project/pillow-avif-plugin/) |
| HEIF | 安装 [pillow-heif](https://pypi.org/project/pillow-heif/)（同时支持 HEIF 和 AVIF） |

---

## 更新日志

查看版本变更记录：[更新日志](./docs/CHANGELOG-1.x.zh.md)

---

## 开源许可

[MIT](./LICENSE) © [SkylerHu](https://github.com/skylerhu)
