#!/usr/bin/env python
# coding=utf-8
from PIL import Image, ImageOps

from imgprocessor.params import ResizeParser, CropParser


def pre_processing(im: Image, use_alpha: bool = False) -> Image:
    """预处理图像，默认转成`RGB`，若为`use_alpha=True`转为`RGBA`

    Args:
        im: 输入图像
        use_alpha: 是否处理透明度

    Returns:
        输出图像
    """
    # 去掉方向信息
    orientation = im.getexif().get(0x0112)
    if orientation and 2 <= orientation <= 8:
        im = ImageOps.exif_transpose(im)

    if im.mode not in ["RGB", "RGBA"]:
        # 统一处理成RGBA进行操作:
        # 1. 像rotate/resize操作需要RGB模式；
        # 2. 像水印操作需要RGBA；
        im = im.convert("RGBA")

    if use_alpha and im.mode != "RGBA":
        im = im.convert("RGBA")

    return im


def action_resize(im: Image, parser: ResizeParser) -> Image:
    im = pre_processing(im)
    size = parser.compute(*im.size)
    if size == im.size:
        # 大小没有变化直接返回
        return im
    out = im.resize(size, resample=Image.LANCZOS)
    return out


def action_crop(im: Image, parser: CropParser) -> Image:
    im = pre_processing(im)
    x, y, w, h = parser.compute(*im.size)

    if x == 0 and y == 0 and (w, h) == im.size:
        # 大小没有变化直接返回
        return im
    im = im.crop((x, y, x + w, y + h))
    return im
