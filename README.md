# py-img-processor

[中文文档](README.zh.md) | **English**

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

**Drive an entire image processing pipeline with a single string parameter or a JSON descriptor.**

py-img-processor is a parameter-driven image processing library built on [Pillow](https://python-pillow.org/), designed for backend services and automation scripts. Describe processing steps as a string or JSON to perform common operations such as resize, crop, watermark, and merge — with both a Python API and the `img-processor` CLI.

---

## Features

- **Resize** — proportional, fixed, pad, fit, and other scaling modes
- **Crop** — coordinates, aspect ratio, and nine-grid positioning
- **Rounded corners** — arbitrary radius, including circular crop
- **Blur** — Gaussian blur
- **Rotate** — any angle from 0–360 degrees
- **Opacity / grayscale**
- **Watermark** — text and image watermarks with tiling, rotation, and opacity
- **Merge / stitch** — foreground / background overlay support
- **Format conversion** — JPEG / PNG / WebP with optional progressive display and quality control
- **Dominant color extraction** — get the main color of an image (HEX)
- **CLI** — ready-to-use `img-processor` command-line tool with batch processing

---

## Requirements

- Python >= 3.9
- Pillow >= 8.0.0

## Installation

```bash
pip install py-img-processor
```

> For HEIF / AVIF and other extended format support, see [Extended Format Support](#extended-format-support) below.

---

## Quick Start

### Python API

```python
from imgprocessor.processor import process_image

# Resize → crop → text watermark → rounded corners → PNG, all in one line
process_image(
    "photo.jpg",
    "resize,s_200/crop,w_200,h_200,g_center/watermark,text_SGVsbG8,color_FFF,size_20/circle,r_10/format,png",
    out_path="output.png",
)
```

Input `photo.jpg` (400x225):

![](./docs/imgs/lenna-400x225.jpg)

Output `output.png` (200x200):

![](./docs/imgs/lenna-edit.png)

> Values in `text_SGVsbG8` must be Base64 URL encoded. Use the built-in helper:
>
> ```python
> from imgprocessor.utils import base64url_encode
> base64url_encode("Hello 世界")  # => "SGVsbG8g5LiW55WM"
> ```

### JSON Parameters (equivalent)

For complex parameters, JSON is recommended — it is more readable, and fields like `text` **do not require Base64 encoding**.

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

### Processing Image Objects Directly

If you already have a Pillow `Image` object, pass it in directly:

```python
from PIL import Image
from imgprocessor.processor import process_image_obj

with Image.open("photo.jpg") as im:
    process_image_obj(im, "resize,s_200/format,webp", out_path="output.webp")
```

### Extracting Dominant Color

```python
from imgprocessor.processor import extract_main_color

extract_main_color("photo.jpg")  # => "905C4C"
```

---

## CLI

After installation, use the `img-processor` command:

```
img-processor -P <input path> --action <action params> -O <output path> [--overwrite]
```

| Parameter | Description |
| --- | --- |
| `-P`, `--path` | Input image file path or directory (batch processing when a directory is given) |
| `--action` | Action parameters (string form); multiple groups allowed |
| `-O`, `--output` | Output path (use an existing directory for multiple images or actions) |
| `--overwrite` | Allow overwriting existing files |
| `-V`, `--version` | Show version number |

**Example: run two action groups on a single image, producing two output files**

```bash
img-processor \
  -P docs/imgs/lenna-400x225.jpg \
  -O /tmp/ \
  --action \
    "resize,s_200/format,webp" \
    "resize,s_225/crop,w_225,h_225,g_center/circle/format,png" \
  --overwrite
```

Output:

`/tmp/lenna-400x225-0.webp` (355x200)

![](./docs/imgs/lenna-400x225-0.webp)

`/tmp/lenna-400x225-1.png` (225x225)

![](./docs/imgs/lenna-400x225-1.png)

---

## Parameter Syntax

### String Format

```
action1,param1_value1,param2_value2/action2,param1_value1
```

| Delimiter | Purpose |
| --- | --- |
| `/` | Separates different actions |
| `,` | Separates parameters within the same action |
| `_` | Separates a parameter key and value |

> When a value is complex (e.g. non-ASCII text, file paths), encode it with `base64url_encode`.

### JSON Format

- Put `format`, `quality`, `interlace`, and `animation` at the top level of the JSON
- Put other actions in the `actions` array; each action is a dict with a `key` field

See [Reference](./docs/Reference.md) or the [online docs](https://py-img-processor.readthedocs.io/) for the full parameter reference.

---

## Configuration

Set the settings module via the `PY_SETTINGS_MODULE` environment variable (`DJANGO_SETTINGS_MODULE` is also supported):

```bash
export PY_SETTINGS_MODULE=your_project.settings
```

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `DEBUG` | bool | `False` | Debug mode |
| `PROCESSOR_MAX_FILE_SIZE` | int | `20` | Maximum source file size (MB) |
| `PROCESSOR_MAX_W_H` | int | `30000` | Maximum width or height in pixels |
| `PROCESSOR_MAX_PIXEL` | int | `300000000` | Maximum total pixels (width × height); also sets Pillow's `MAX_IMAGE_PIXELS` |
| `PROCESSOR_DEFAULT_QUALITY` | int | `75` | Default output quality |
| `PROCESSOR_TEXT_FONT` | str | `Arial Unicode.ttf` | Font for text watermarks; use an absolute path to a font file when possible |
| `PROCESSOR_WORKSPACES` | tuple | `()` | Directories allowed for watermarks and other resources (`startswith` match) |
| `PROCESSOR_ALLOW_DOMAINS` | tuple | `()` | Domain whitelist for URL resources (`endswith` match) |
| `PROCESSOR_TEMP_DIR` | str | `None` | Temporary file directory; system default if unset |

> **Note**: `PROCESSOR_TEXT_FONT` is required for text watermarks — ensure the font is installed on the system, or set it to a font file path. The default `Arial Unicode.ttf` is only available on macOS.

---

## Extended Format Support

This library is built on Pillow and supports JPEG, PNG, and WebP by default. To handle HEIF (`.heic`) or AVIF (`.avif`), install a plugin:

| Format | Approach |
| --- | --- |
| AVIF | Built into Pillow >= 12.0.0; on older versions install [pillow-avif-plugin](https://pypi.org/project/pillow-avif-plugin/) |
| HEIF | Install [pillow-heif](https://pypi.org/project/pillow-heif/) (supports both HEIF and AVIF) |

---

## Changelog

See version history: [CHANGELOG](./docs/CHANGELOG-1.x.md)

---

## License

[MIT](./LICENSE) © [SkylerHu](https://github.com/skylerhu)
