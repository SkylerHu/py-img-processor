#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image

from imgprocessor import enums, settings
from .base import BaseParser


class WatermarkParser(BaseParser):

    KEY = enums.OpAction.WATERMARK
    ARGS = {
        # 水印本身的不透明度，100表示完全不透明
        "t": {"type": enums.ArgType.INTEGER, "default": 100, "min": 0, "max": 100},
        "g": {"type": enums.ArgType.STRING, "choices": enums.Geography},
        "x": {"type": enums.ArgType.INTEGER, "default": 10, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "y": {"type": enums.ArgType.INTEGER, "default": 10, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # percent field, eg: xy
        "pf": {"type": enums.ArgType.STRING, "default": ""},
        # 是否将图片水印或文字水印铺满原图; 值为1开启
        "fill": {"type": enums.ArgType.INTEGER, "default": 0, "choices": [0, 1]},
        "padx": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "pady": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # 图片水印路径
        "image": {"type": enums.ArgType.STRING, "enable_base64": True},
        # 指定图片水印按照要添加水印的原图的比例进行缩放
        "P": {"type": enums.ArgType.INTEGER, "default": None, "min": 1, "max": 100},
        # 文字
        "text": {"type": enums.ArgType.STRING, "enable_base64": True},
        "type": {"type": enums.ArgType.STRING, "enable_base64": True},
        "color": {"type": enums.ArgType.STRING, "default": "000000", "regex": "^([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$"},
        "size": {"type": enums.ArgType.INTEGER, "default": 40, "min": 1, "max": 1000},
        # 文字水印的阴影透明度, 0表示没有阴影
        "shadow": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 100},
        # 文字顺时针旋转角度
        "rotate": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 360},
        # 图文混合水印参数
        # 文字和图片水印的前后顺序; 0表示图片水印在前；1表示文字水印在前
        "order": {"type": enums.ArgType.INTEGER, "default": 0, "choices": enums.ImgOrder},
        # 文字水印和图片水印的对齐方式; 0表示文字水印和图片水印上对齐; 1表示文字水印和图片水印中对齐; 2: 表示文字水印和图片水印下对齐
        "align": {"type": enums.ArgType.INTEGER, "default": 2, "choices": enums.ImgAlign},
        # 文字水印和图片水印间的间距
        "interval": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 1000},
    }

    def __init__(
        self,
        t: int = 100,
        g: typing.Optional[str] = None,
        x: int = 10,
        y: int = 10,
        pf: str = "",
        fill: int = 0,
        padx: int = 0,
        pady: int = 0,
        image: typing.Optional[str] = None,
        P: typing.Optional[int] = None,
        text: typing.Optional[str] = None,
        type: typing.Optional[str] = None,
        color: str = "000000",
        size: int = 40,
        shadow: int = 0,
        rotate: int = 0,
        order: int = 0,
        align: int = 2,
        interval: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.t = t
        self.g = g
        self.x = x
        self.y = y
        self.pf = pf
        self.fill = fill
        self.padx = padx
        self.pady = pady
        self.image = image
        self.P = P
        self.text = text
        self.type = type
        self.color = color
        self.size = size
        self.shadow = shadow
        self.rotate = rotate
        self.order = order
        self.align = align
        self.interval = interval

    def do_action(self, im: Image) -> Image:
        return im
