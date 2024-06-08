#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import exceptions, enums


def action_resize(
    src_w: int,
    src_h: int,
    m: str = enums.ResizeMode.LFIT,
    w: int = 0,
    h: int = 0,
    l: int = 1,
    s: int = 1,
    limit: int = 1,
    color: str = "FFFFFF",
    p: int = 0,
    **kwargs: typing.Any,
) -> tuple:
    if w or h:
        if m == enums.ResizeMode.FIXED:
            # 有可能改变原图宽高比
            if not (w > 0 and h > 0):
                raise exceptions.ParamValidateException(f"当m={m}的模式下，参数w和h都必不可少且不能为0")
            # w,h按指定的即可，无需计算
        elif m == enums.ResizeMode.LFIT:
            pass
    elif l:
        # 按最长边缩放
        if src_w > src_h:
            w, h = l, int(src_h * l / src_w)
        else:
            w, h = int(src_w * l / src_h), l
    elif s:
        # 按最短边缩放
        if src_w > src_h:
            w, h = int(src_w * s / src_h), s
        else:
            w, h = s, int(src_h * s / src_w)
    elif p:
        # 按照比例缩放
        if 1 <= p <= 1000:
            w, h = int(src_w * p / 100), int(src_h * p / 100)
        else:
            raise exceptions.ParamValidateException(
                "p的取值范围为[1,1000]，小于100为缩小，大于100为放大"
            )
    else:
        # 缺少参数
        raise exceptions.ParamValidateException("resize操作缺少合法参数")
