# FAQ

## General

### What Python versions are supported?

Python 3.9 and above. Pillow 8.0.0 or later is required.

### How do I install py-img-processor?

```bash
pip install py-img-processor
```

### What image formats are supported?

JPEG, PNG, and WebP are supported out of the box. For HEIF (`.heic`) or AVIF (`.avif`), see [Extended Format Support](#how-do-i-add-heif-or-avif-support).

---

## Image Processing

### How do I chain multiple operations?

Use `/` to separate actions. Each action is processed in order from left to right:

```python
from imgprocessor.processor import process_image

process_image(
    "input.jpg",
    "resize,s_300/crop,w_300,h_300,g_center/circle,r_20/format,png",
    out_path="output.png",
)
```

This resizes → crops → rounds corners → converts to PNG in a single pipeline.

### How do I use JSON parameters instead of a string?

JSON is recommended when parameters are complex. The `text` field does **not** require Base64 encoding in JSON mode:

```python
process_image(
    "input.jpg",
    {
        "actions": [
            {"key": "resize", "w": 800},
            {"key": "watermark", "text": "Hello World", "color": "FFF", "size": 24},
        ],
        "format": "webp",
        "quality": 80,
    },
    out_path="output.webp",
)
```

### How do I handle Chinese or special characters in text watermarks?

**String mode**: encode the text with `base64url_encode`:

```python
from imgprocessor.utils import base64url_encode

encoded = base64url_encode("你好世界")
action = f"watermark,text_{encoded},size_20,color_333"
```

**JSON mode**: pass the text directly — no encoding needed:

```python
{"key": "watermark", "text": "你好世界", "size": 20, "color": "333"}
```

### How do I extract the dominant color of an image?

```python
from imgprocessor.processor import extract_main_color

hex_color = extract_main_color("photo.jpg")  # => "905C4C"
```

### How do I process a Pillow Image object directly?

Use `process_image_obj` instead of `process_image`:

```python
from PIL import Image
from imgprocessor.processor import process_image_obj

with Image.open("photo.jpg") as im:
    result = process_image_obj(im, "resize,s_200/format,webp", out_path="out.webp")
```

---

## Configuration

### How do I change the maximum allowed file size?

Set `PROCESSOR_MAX_FILE_SIZE` in your settings module (default is 20 MB):

```python
# your_project/settings.py
PROCESSOR_MAX_FILE_SIZE = 50  # MB
```

Then export the module:

```bash
export PY_SETTINGS_MODULE=your_project.settings
```

### Which font is used for text watermarks?

The default is `Arial Unicode.ttf` (available on macOS). On Linux servers, set `PROCESSOR_TEXT_FONT` to an absolute path of an installed font:

```python
PROCESSOR_TEXT_FONT = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
```

### How do I use py-img-processor with Django?

Set `DJANGO_SETTINGS_MODULE` as usual — py-img-processor recognizes it automatically. Add the configuration keys to your Django settings:

```python
# settings.py
PROCESSOR_MAX_FILE_SIZE = 10
PROCESSOR_DEFAULT_QUALITY = 80
PROCESSOR_TEXT_FONT = "/path/to/font.ttf"
```

---

## Formats

### How do I add HEIF or AVIF support?

| Format | Approach |
| --- | --- |
| AVIF | Built into Pillow >= 12.0.0; on older versions install [pillow-avif-plugin](https://pypi.org/project/pillow-avif-plugin/) |
| HEIF | Install [pillow-heif](https://pypi.org/project/pillow-heif/) (supports both HEIF and AVIF) |

### What is the difference between `quality` and `interlace`?

- `quality` controls lossy compression level (1–100). Lower values produce smaller files but more artifacts. Only works with JPEG and WebP.
- `interlace` enables progressive display (`interlace,1`). The image loads as a low-res preview first, then gradually sharpens — useful for large images on slow connections.

---

## CLI

### How do I batch-process all images in a directory?

Pass a directory to `-P` and a directory to `-O`:

```bash
img-processor -P ./photos/ --action "resize,s_800/format,webp" -O ./output/ --overwrite
```

### Can I apply multiple action groups to the same image?

Yes, pass multiple `--action` arguments. Each produces a separate output file:

```bash
img-processor -P photo.jpg -O /tmp/ --action "resize,s_200/format,webp" "resize,s_400/format,png"
```

---

## Troubleshooting

### I get "font not found" errors with text watermarks

Ensure the font file exists at the path specified by `PROCESSOR_TEXT_FONT`. On Linux, install a Unicode font:

```bash
# Ubuntu/Debian
sudo apt install fonts-noto-cjk

# Then set
PROCESSOR_TEXT_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
```

### Large images cause memory errors

Adjust the pixel limits in your settings:

```python
PROCESSOR_MAX_PIXEL = 300000000    # Maximum total pixels (width × height)
PROCESSOR_MAX_W_H = 30000         # Maximum single dimension
```

For extremely large images, consider resizing before applying other operations.

### The output image quality is too low

Increase the `quality` parameter (default is 75):

```python
process_image("input.jpg", "quality,90/format,jpeg", out_path="output.jpg")
```

Or set the global default:

```python
PROCESSOR_DEFAULT_QUALITY = 90
```
