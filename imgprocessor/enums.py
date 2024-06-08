#!/usr/bin/env python
# coding=utf-8
from py_enum import ChoiceEnum


class ImageType(ChoiceEnum):
    JPEG = ("JPEG", "JPEG")
    PNG = ("PNG", "PNG")
    WEBP = ("WebP", "WebP")


class OpAction(ChoiceEnum):
    """支持的操作类型"""

    # 以下2个比较特殊，在保存文件时使用
    QUALITY = ("quality", "质量")
    FORMAT = ("format", "格式")
    # 其他
    CROP = ("crop", "裁剪")
    RESIZE = ("resize", "缩放")


class ResizeMode(ChoiceEnum):
    LFIT = ("lfit", "等比缩放，缩放图限制为指定w与h的矩形内的最大图片")
    MFIT = ("mfit", "等比缩放，缩放图为延伸出指定w与h的矩形框外的最小图片")
    FILL = ("fill", "将原图等比缩放为延伸出指定w与h的矩形框外的最小图片，然后将超出的部分进行居中裁剪")
    PAD = ("pad", "将原图缩放为指定w与h的矩形内的最大图片，然后使用指定颜色居中填充空白部分")
    FIXED = ("fixed", "固定宽高，强制缩放")


class ArgType(ChoiceEnum):
    INTEGER = ("int", "整数")
    FLOAT = ("float", "浮点数")
    STRING = ("str", "字符串")
    CHOICES = ("choices", "枚举值")
    BOOLEAN = ("bool", "布尔值")
