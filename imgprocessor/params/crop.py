#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import enums, settings
from imgprocessor.exceptions import ParamValidateException
from .base import BaseParser


class CropParser(BaseParser):

    key = enums.OpAction.CROP
    ARGS = {
        "w": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "h": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "x": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "y": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "g": {"type": enums.ArgType.CHOICES, "choices": enums.Geography},
        # percent field, eg: xywh
        "pf": {"type": enums.ArgType.STRING, "default": ""},
        # padding right
        "pr": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # padding bottom
        "pb": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # 左和上通过x,y控制
    }

    def __init__(
        self,
        w: int = 0,
        h: int = 0,
        x: int = 0,
        y: int = 0,
        g: str = "",
        pf: str = "",
        pr: int = 0,
        pb: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.g = g
        self.pf = pf
        self.pr = pr
        self.pb = pb

    def compute(self, src_w: int, src_h: int) -> tuple:
        x, y, w, h = self.x, self.y, self.w, self.h

        pf = self.pf or ""
        if self.g:
            # g在的时候pf不生效
            pf = ""

        # 处理w,h，w,h默认原图大小
        if "w" in pf:
            if w < 0 or w > 100:
                raise ParamValidateException(f"pf={pf}包含了w，所以w作为百分比取值范围为[0,100]")
            w = int(src_w * w / 100)
        elif not w:
            w = src_w

        if "h" in pf:
            if h < 0 or h > 100:
                raise ParamValidateException(f"pf={pf}包含了h，所以h作为百分比取值范围为[0,100]")
            h = int(src_h * h / 100)
        elif not h:
            h = src_h

        # 按照其他方式计算x,y
        if self.g == enums.Geography.NW:
            x, y = 0, 0
        elif self.g == enums.Geography.NORTH:
            x, y = int(src_w / 2 - w / 2), 0
        elif self.g == enums.Geography.NE:
            x, y = src_w - w, 0
        elif self.g == enums.Geography.WEST:
            x, y = 0, int(src_h / 2 - h / 2)
        elif self.g == enums.Geography.CENTER:
            x, y = int(src_w / 2 - w / 2), int(src_h / 2 - h / 2)
        elif self.g == enums.Geography.EAST:
            x, y = src_w - w, int(src_h / 2 - h / 2)
        elif self.g == enums.Geography.SW:
            x, y = 0, src_h - h
        elif self.g == enums.Geography.SOUTH:
            x, y = int(src_w / 2 - w / 2), src_h - h
        elif self.g == enums.Geography.SE:
            x, y = src_w - w, src_h - h
        elif pf:
            if "x" in pf:
                if x < 0 or x > 100:
                    raise ParamValidateException(f"pf={pf}包含了x，所以x作为百分比取值范围为[0,100]")
                x = int(src_w * x / 100)
            if "y" in pf:
                if y < 0 or y > 100:
                    raise ParamValidateException(f"pf={pf}包含了y，所以y作为百分比取值范围为[0,100]")
                y = int(src_h * y / 100)

        # 处理裁边
        if self.pr:
            w = w - self.pr
        if self.pb:
            h = h - self.pb

        if x < 0 or y < 0 or w < 0 or y < 0 or x + w > src_w or y + h > src_h:
            raise ParamValidateException(f"(x, y, w, h)={(x, y, w, h)} 区域超过了原始图片")

        return x, y, w, h
