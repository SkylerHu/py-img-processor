#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image

from imgprocessor import enums
from .base import BaseParser, pre_processing


class AlphaParser(BaseParser):

    KEY = enums.OpAction.ALPHA
    ARGS = {
        # 不透明度, 为100时，完全不透明，即原图; 为0时，完全透明
        "value": {"type": enums.ArgType.INTEGER, "default": 100, "min": 0, "max": 100},
    }

    def __init__(
        self,
        value: int = 100,
        **kwargs: typing.Any,
    ) -> None:
        self.value = value

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im, use_alpha=True)
        if self.value < 100:
            _, _, _, alpha_channel = im.split()
            alpha_channel = alpha_channel.point(lambda i: min(int(255 * self.value / 100), i))
            im.putalpha(alpha_channel)
        return im
