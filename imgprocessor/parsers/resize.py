#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image, ImageOps
from imgprocessor import enums, settings
from imgprocessor.exceptions import ParamValidateException, ProcessLimitException
from .base import BaseParser, pre_processing


class ResizeParser(BaseParser):

    KEY = enums.OpAction.RESIZE
    ARGS = {
        "m": {"type": enums.ArgType.STRING, "default": enums.ResizeMode.LFIT, "choices": enums.ResizeMode},
        "w": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "h": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "l": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "s": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "limit": {"type": enums.ArgType.INTEGER, "default": 1, "choices": [0, 1]},
        "color": {
            "type": enums.ArgType.STRING,
            "default": "FFFFFF",  # 默认白色
            "regex": r"^([0-9a-fA-F]{6}|[0-9a-fA-F]{8}|[0-9a-fA-F]{3,4})$",
        },
        "p": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": 1000},
    }

    def __init__(
        self,
        m: str = enums.ResizeMode.LFIT,  # type: ignore
        w: int = 0,
        h: int = 0,
        l: int = 0,  # noqa: E741
        s: int = 0,
        limit: int = 1,
        color: str = "FFFFFF",
        p: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.m = m
        self.w = w
        self.h = h
        self.l = l  # noqa: E741
        self.s = s
        self.limit = limit
        self.color = color
        self.p = p

    def compute(self, src_w: int, src_h: int) -> tuple:
        """计算出`Image.resize`需要的参数"""
        if self.w or self.h:
            if self.m in [enums.ResizeMode.FIXED, enums.ResizeMode.PAD, enums.ResizeMode.FIT]:
                # 有可能改变原图宽高比
                if not (self.w and self.h):
                    raise ParamValidateException(f"当m={self.m}的模式下，参数w和h都必不可少且不能为0")
                # w,h按指定的即可，无需计算
                w, h = self.w, self.h
            elif self.m == enums.ResizeMode.MFIT:
                # 低版本Pillow未实现 ImageOps.cover 方法，自行处理
                # 等比缩放
                if self.w and self.h:
                    # 指定w与h的矩形外的最小图像
                    if self.w / self.h > src_w / src_h:
                        w, h = self.w, round(self.w * src_h / src_w)
                    else:
                        w, h = round(self.h * src_w / src_h), self.h
                elif self.w:
                    w, h = self.w, round(self.w * src_h / src_w)
                else:
                    w, h = round(self.h * src_w / src_h), self.h
            else:
                # 默认 enums.ResizeMode.LFIT
                # 等比缩放
                if self.w and self.h:
                    # 指定w与h的矩形内的最大图像
                    if self.w / self.h > src_w / src_h:
                        w, h = round(self.h * src_w / src_h), self.h
                    else:
                        w, h = self.w, round(self.w * src_h / src_w)
                elif self.w:
                    w, h = self.w, round(self.w * src_h / src_w)
                else:
                    w, h = round(self.h * src_w / src_h), self.h
        elif self.l:
            # 按最长边缩放
            if src_w > src_h:
                w, h = self.l, round(src_h * self.l / src_w)
            else:
                w, h = round(src_w * self.l / src_h), self.l
        elif self.s:
            # 按最短边缩放
            if src_w > src_h:
                w, h = round(src_w * self.s / src_h), self.s
            else:
                w, h = self.s, round(src_h * self.s / src_w)
        elif self.p:
            # 按照比例缩放
            w, h = round(src_w * self.p / 100), round(src_h * self.p / 100)
        else:
            # 缺少参数
            raise ParamValidateException("resize操作缺少合法参数")

        if self.limit and (w > src_w or h > src_h):
            # 超过原图大小，默认不处理
            w, h = (src_w, src_h)
        elif w * h > settings.PROCESSOR_MAX_PIXEL:
            raise ProcessLimitException(f"缩放的目标图像总像素不可超过{settings.PROCESSOR_MAX_PIXEL}像素")
        return (w, h)

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im)
        size = self.compute(*im.size)
        if size == im.size:
            # 大小没有变化直接返回
            return im
        if self.m == enums.ResizeMode.PAD:
            out = ImageOps.pad(im, size, color=f"#{self.color}")
        elif self.m == enums.ResizeMode.FIT:
            out = ImageOps.fit(im, size)
        else:
            out = im.resize(size, resample=Image.LANCZOS)
        return out
