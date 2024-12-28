#!/usr/bin/env python
# coding=utf-8
from py_enum import ChoiceEnum


class ImageFormat(ChoiceEnum):
    """图像转换的格式"""

    JPEG = ("JPEG", "JPEG")
    PNG = ("PNG", "PNG")
    WEBP = ("WebP", "WebP")


class ImageOrientation(ChoiceEnum):
    """
    图片EXIF中的方向枚举，第0行0列的位置(即图像正常显示右上角的位置)

    see http://sylvana.net/jpegcrop/exif_orientation.html
    """

    TOP_LEFT = (1, "0度：正确方向，无需调整")
    TOP_RIGHT = (2, "水平翻转")
    BOTTOM_RIGHT = (3, "180度旋转")
    BOTTOM_LEFT = (4, "水平翻转+180度旋转")  # 垂直翻转
    LEFT_TOP = (5, "水平翻转+顺时针270度")
    RIGHT_TOP = (6, "顺时针270度")
    RIGHT_BOTTOM = (7, "水平翻转+顺时针90度")
    LEFT_BOTTOM = (8, "顺时针90°")


class OpAction(ChoiceEnum):
    """支持的操作类型"""

    # 以下几个比较特殊，在保存文件时使用
    FORMAT = ("format", "格式")
    QUALITY = ("quality", "质量")
    INTERLACE = ("interlace", "渐进显示")
    # 其他
    RESIZE = ("resize", "缩放")
    CROP = ("crop", "裁剪")
    CIRCLE = ("circle", "圆角")
    BLUR = ("blur", "模糊效果")
    ROTATE = ("rotate", "旋转")
    ALPHA = ("alpha", "透明度")
    GRAY = ("gray", "灰度图")
    WATERMARK = ("watermark", "水印")
    # 特殊操作
    MERGE = ("merge", "合并图像")


class ResizeMode(ChoiceEnum):
    """图像缩放的模式"""

    LFIT = ("lfit", "等比缩放，缩放图限制为指定w与h的矩形内的最大图片")  # 类似 ImageOps.contain
    MFIT = ("mfit", "等比缩放，缩放图为延伸出指定w与h的矩形框外的最小图片")  # 类似 ImageOps.cover
    FIT = ("fit", "将原图等比缩放为延伸出指定w与h的矩形框外的最小图片，然后将超出的部分进行居中裁剪")  # ImageOps.fit
    PAD = ("pad", "将原图缩放为指定w与h的矩形内的最大图片，然后使用指定颜色居中填充空白部分")  # ImageOps.pad
    FIXED = ("fixed", "固定宽高，强制缩放")


class ArgType(ChoiceEnum):
    STRING = ("str", "字符串")
    INTEGER = ("int", "整数")
    FLOAT = ("float", "浮点数")
    URI = ("uri", "资源路径/链接")
    ACTION = ("action", "对图像的操作")


class Geography(ChoiceEnum):
    """图像中的九宫格位置"""

    NW = ("nw", "左上")
    NORTH = ("north", "中上")
    NE = ("ne", "右上")
    WEST = ("west", "左中")
    CENTER = ("center", "中部")
    EAST = ("east", "右中")
    SW = ("sw", "左下")
    SOUTH = ("south", "中下")
    SE = ("se", "右下")


class PositionOrder(ChoiceEnum):
    """两个元素的前后顺序"""

    BEFORE = (0, "第一输入元素在前/在上")  # 图片在前
    AFTER = (1, "第一个输入元素在后/在下")  # 文字在前


class PositionAlign(ChoiceEnum):
    """两个元素的对齐方式"""

    TOP = (0, "水平上对齐")
    HORIZONTAL_CENTER = (1, "水平居中对齐")
    BOTTOM = (2, "水平下对齐")
    LEFT = (3, "垂直左对齐")
    VERTIAL_CENTER = (4, "垂直居中对齐")
    RIGHT = (5, "垂直右对齐")
