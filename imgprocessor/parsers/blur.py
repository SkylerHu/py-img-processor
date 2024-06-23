#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image, ImageFilter

from imgprocessor import enums
from .base import BaseParser, pre_processing


class BlurParser(BaseParser):

    KEY = enums.OpAction.BLUR
    ARGS = {
        # 模糊半径，值越大，图片越模糊
        "r": {"type": enums.ArgType.INTEGER, "required": True, "min": 1, "max": 50},
    }

    def __init__(
        self,
        r: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.r = r

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im)
        im = im.filter(ImageFilter.GaussianBlur(radius=self.r))
        return im
