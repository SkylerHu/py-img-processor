#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image

from imgprocessor import enums
from .base import BaseParser, pre_processing


class RotateParser(BaseParser):

    KEY = enums.OpAction.ROTATE
    ARGS = {
        # 顺时针旋转的度数
        "value": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 360},
    }

    def __init__(
        self,
        value: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.value = value

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im)
        if 0 < self.value < 360:
            # 函数提供的是逆时针旋转
            im = im.rotate(360 - self.value, expand=True)
        return im
