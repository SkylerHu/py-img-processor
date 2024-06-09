#!/usr/bin/env python
# coding=utf-8
from PIL import Image

from imgprocessor.params import ResizeAction


def action_resize(img: Image, action: ResizeAction) -> Image:
    size = action.compute(*img.size)
    out = img.resize(size, resample=Image.Resampling.LANCZOS)
    return out
