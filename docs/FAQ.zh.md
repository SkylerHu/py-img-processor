# 常见问题

## 基础

### 支持哪些 Python 版本？

Python 3.9 及以上，需要 Pillow 8.0.0 或更高版本。

### 如何安装 py-img-processor？

```bash
pip install py-img-processor
```

### 支持哪些图片格式？

默认支持 JPEG、PNG 和 WebP。如需处理 HEIF（`.heic`）或 AVIF（`.avif`），请参见 [扩展格式支持](#heif-avif)。

---

## 图像处理

### 如何链式执行多个操作？

使用 `/` 分隔不同操作，按从左到右的顺序依次执行：

```python
from imgprocessor.processor import process_image

process_image(
    "input.jpg",
    "resize,s_300/crop,w_300,h_300,g_center/circle,r_20/format,png",
    out_path="output.png",
)
```

以上一行完成缩放 → 裁剪 → 圆角 → 转 PNG 的完整流水线。

### 如何使用 JSON 参数代替字符串？

当参数较复杂时推荐使用 JSON。JSON 模式下 `text` 字段**无需** Base64 编码：

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

### 文字水印中如何处理中文或特殊字符？

**字符串模式**：使用 `base64url_encode` 编码文本：

```python
from imgprocessor.utils import base64url_encode

encoded = base64url_encode("你好世界")
action = f"watermark,text_{encoded},size_20,color_333"
```

**JSON 模式**：直接传入原始文本，无需编码：

```python
{"key": "watermark", "text": "你好世界", "size": 20, "color": "333"}
```

### 如何提取图片主色调？

```python
from imgprocessor.processor import extract_main_color

hex_color = extract_main_color("photo.jpg")  # => "905C4C"
```

### 如何直接处理 Pillow Image 对象？

使用 `process_image_obj` 代替 `process_image`：

```python
from PIL import Image
from imgprocessor.processor import process_image_obj

with Image.open("photo.jpg") as im:
    result = process_image_obj(im, "resize,s_200/format,webp", out_path="out.webp")
```

---

## 配置

### 如何修改允许的最大文件大小？

在配置模块中设置 `PROCESSOR_MAX_FILE_SIZE`（默认 20 MB）：

```python
# your_project/settings.py
PROCESSOR_MAX_FILE_SIZE = 50  # MB
```

然后导出配置模块：

```bash
export PY_SETTINGS_MODULE=your_project.settings
```

### 文字水印使用哪种字体？

默认使用 `Arial Unicode.ttf`（仅 macOS 自带）。在 Linux 服务器上，需将 `PROCESSOR_TEXT_FONT` 设为字体文件的绝对路径：

```python
PROCESSOR_TEXT_FONT = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
```

### 如何在 Django 项目中使用？

正常设置 `DJANGO_SETTINGS_MODULE` 即可，py-img-processor 会自动识别。在 Django settings 中添加配置项：

```python
# settings.py
PROCESSOR_MAX_FILE_SIZE = 10
PROCESSOR_DEFAULT_QUALITY = 80
PROCESSOR_TEXT_FONT = "/path/to/font.ttf"
```

---

## 格式

### 如何支持 HEIF 或 AVIF 格式？

| 格式 | 方式 |
| --- | --- |
| AVIF | Pillow >= 12.0.0 内置支持；旧版本可安装 [pillow-avif-plugin](https://pypi.org/project/pillow-avif-plugin/) |
| HEIF | 安装 [pillow-heif](https://pypi.org/project/pillow-heif/)（同时支持 HEIF 和 AVIF） |

### `quality` 和 `interlace` 有什么区别？

- `quality` 控制有损压缩级别（1–100），值越低文件越小但画质下降。仅对 JPEG 和 WebP 有效。
- `interlace` 启用渐进式显示（`interlace,1`），图片先以低分辨率预览加载，然后逐步变清晰——适用于大图在慢速网络下的加载体验。

---

## 命令行

### 如何批量处理目录下的所有图片？

将目录路径传给 `-P`，输出目录传给 `-O`：

```bash
img-processor -P ./photos/ --action "resize,s_800/format,webp" -O ./output/ --overwrite
```

### 同一张图片能同时生成多种规格吗？

可以，传入多个 `--action` 参数，每个参数组生成一个独立的输出文件：

```bash
img-processor -P photo.jpg -O /tmp/ --action "resize,s_200/format,webp" "resize,s_400/format,png"
```

---

## 常见问题排查

### 文字水印报 "font not found" 错误

确保 `PROCESSOR_TEXT_FONT` 指定的字体文件路径存在。Linux 下可安装 Unicode 字体：

```bash
# Ubuntu/Debian
sudo apt install fonts-noto-cjk

# 然后设置
PROCESSOR_TEXT_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
```

### 处理大尺寸图片时内存不足

在配置中调整像素限制：

```python
PROCESSOR_MAX_PIXEL = 300000000    # 最大总像素（宽 × 高）
PROCESSOR_MAX_W_H = 30000         # 单边最大尺寸
```

对于超大图片，建议先缩放再执行其他操作。

### 输出图片质量太低

提高 `quality` 参数（默认值为 75）：

```python
process_image("input.jpg", "quality,90/format,jpeg", out_path="output.jpg")
```

或修改全局默认值：

```python
PROCESSOR_DEFAULT_QUALITY = 90
```
