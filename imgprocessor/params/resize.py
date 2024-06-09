#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import enums, settings
from imgprocessor.exceptions import ParamValidateException
from .base import BaseParser


class ResizeAction(BaseParser):

    key = enums.OpAction.RESIZE
    ARGS = {
        "m": {"type": enums.ArgType.CHOICES, "default": enums.ResizeMode.LFIT, "choices": enums.ResizeMode},
        "w": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "h": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "l": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "s": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "limit": {"type": enums.ArgType.INTEGER, "default": 1, "min": 0, "max": 1},
        "color": {"type": enums.ArgType.STRING, "default": "FFFFFF", "regex": "^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$"},
        "p": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": 1000},
    }

    def __init__(
        self,
        m: str = enums.ResizeMode.LFIT,  # type: ignore
        w: int = 0,
        h: int = 0,
        l: int = 1,  # noqa: E741
        s: int = 1,
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
            if self.m == enums.ResizeMode.FIXED:
                # 有可能改变原图宽高比
                if not (self.w and self.h):
                    raise ParamValidateException(f"当m={self.m}的模式下，参数w和h都必不可少且不能为0")
                # w,h按指定的即可，无需计算
                w, h = self.w, self.h
            elif self.m == enums.ResizeMode.MFIT:
                # 等比缩放
                if self.w and self.h:
                    # 指定w与h的矩形外的最小图片
                    if self.w / self.h > src_w / src_h:
                        w, h = self.w, int(self.w * src_h / src_w)
                    else:
                        w, h = int(self.h * src_w / src_h), self.h
                elif self.w:
                    w, h = self.w, int(self.w * src_h / src_w)
                else:
                    w, h = int(self.h * src_w / src_h), self.h
            else:
                # 默认enums.ResizeMode.LFIT
                # 等比缩放
                if self.w and self.h:
                    # 指定w与h的矩形内的最大图片
                    if self.w / self.h > src_w / src_h:
                        w, h = int(self.h * src_w / src_h), self.h
                    else:
                        w, h = self.w, int(self.w * src_h / src_w)
                elif self.w:
                    w, h = self.w, int(self.w * src_h / src_w)
                else:
                    w, h = int(self.h * src_w / src_h), self.h
        elif self.l:
            # 按最长边缩放
            if src_w > src_h:
                w, h = self.l, int(src_h * self.l / src_w)
            else:
                w, h = int(src_w * self.l / src_h), self.l
        elif self.s:
            # 按最短边缩放
            if src_w > src_h:
                w, h = int(src_w * self.s / src_h), self.s
            else:
                w, h = self.s, int(src_h * self.s / src_w)
        elif self.p:
            # 按照比例缩放
            w, h = int(src_w * self.p / 100), int(src_h * self.p / 100)
        else:
            # 缺少参数
            raise ParamValidateException("resize操作缺少合法参数")

        return (w, h)
