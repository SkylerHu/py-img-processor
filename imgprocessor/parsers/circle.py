#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image, ImageDraw

from imgprocessor import enums, settings
from .base import BaseParser, pre_processing


class CircleParser(BaseParser):

    KEY = enums.OpAction.CIRCLE
    ARGS = {
        "r": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
    }

    def __init__(
        self,
        r: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.r = r

    def compute(self, src_w: int, src_h: int) -> int:
        r = self.r

        min_s = int(min(src_w, src_h) / 2)
        if not r or r > min_s:
            # 没有设置或是超过最大内切圆的半径，按照最大内切圆的半径处理
            r = min_s

        return r

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im, use_alpha=True)

        src_w, src_h = im.size
        rad = self.compute(*im.size)
        # 放大倍数，解决圆角锯齿问题
        expand = 6
        new_rad = rad * expand
        circle = Image.new("L", (new_rad * 2, new_rad * 2), 0)
        ImageDraw.Draw(circle).ellipse((0, 0, new_rad * 2, new_rad * 2), fill=255)
        circle = circle.resize((rad * 2, rad * 2), resample=Image.LANCZOS)

        alpha = Image.new("L", (src_w, src_h), 255)
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, src_h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (src_w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (src_w - rad, src_h - rad))
        im.putalpha(alpha)
        return im
