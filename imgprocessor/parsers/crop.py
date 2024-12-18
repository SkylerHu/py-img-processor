#!/usr/bin/env python
# coding=utf-8
import typing
from PIL import Image
from imgprocessor import enums, settings
from imgprocessor.exceptions import ParamValidateException
from .base import BaseParser, pre_processing, compute_by_geography, compute_by_ratio


class CropParser(BaseParser):

    KEY = enums.OpAction.CROP
    ARGS = {
        "w": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "h": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "ratio": {"type": enums.ArgType.STRING, "regex": r"^\d+:\d+$"},
        "x": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "y": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "g": {"type": enums.ArgType.STRING, "choices": enums.Geography},
        # percent field, eg: xywh
        "pf": {"type": enums.ArgType.STRING, "default": ""},
        # padding right
        "padr": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # padding bottom
        "padb": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # 左和上通过x,y控制
    }

    def __init__(
        self,
        w: int = 0,
        h: int = 0,
        ratio: typing.Optional[str] = None,
        x: int = 0,
        y: int = 0,
        g: typing.Optional[str] = None,
        pf: str = "",
        padr: int = 0,
        padb: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.w = w
        self.h = h
        self.ratio = ratio
        self.x = x
        self.y = y
        self.g = g
        self.pf = pf
        self.padr = padr
        self.padb = padb

    def compute(self, src_w: int, src_h: int) -> tuple:
        x, y, w, h = self.x, self.y, self.w, self.h

        pf = self.pf or ""
        if self.g:
            # g在的时候pf不生效
            pf = ""

        # 处理w,h; w,h默认原图大小
        if self.ratio:
            w, h = compute_by_ratio(src_w, src_h, self.ratio)
        else:
            if "w" in pf:
                if w < 0 or w > 100:
                    raise ParamValidateException(f"pf={pf}包含了w，所以w作为百分比取值范围为[0,100]")
                w = round(src_w * w / 100)
            elif not w:
                w = src_w

            if "h" in pf:
                if h < 0 or h > 100:
                    raise ParamValidateException(f"pf={pf}包含了h，所以h作为百分比取值范围为[0,100]")
                h = round(src_h * h / 100)
            elif not h:
                h = src_h

        # 按照其他方式计算x,y
        x, y = compute_by_geography(src_w, src_h, x, y, w, h, self.g, pf)

        # 处理裁边
        if self.padr:
            w = w - self.padr
        if self.padb:
            h = h - self.padb

        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > src_w or y + h > src_h:
            raise ParamValidateException(f"(x, y, w, h)={(x, y, w, h)} 区域超过了原始图片")

        return x, y, w, h

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im)
        x, y, w, h = self.compute(*im.size)

        if x == 0 and y == 0 and (w, h) == im.size:
            # 大小没有变化直接返回
            return im
        im = im.crop((x, y, x + w, y + h))
        return im
