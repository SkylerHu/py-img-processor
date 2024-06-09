#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image, ImageOps

from imgprocessor.params import ProcessParams


def process_image_by_path(input_path: str, out_path: str, params: typing.Union[ProcessParams, dict]) -> None:
    if isinstance(params, dict):
        params = ProcessParams(**params)
    params = typing.cast(ProcessParams, params)

    im = Image.open(input_path)
    # ori_im = im
    if im.mode != "RGBA":
        # 统一处理成RGBA进行操作:
        # - 像rotate/resize操作需要RGB模式；
        # - 像水印操作需要RGBA；
        im = im.convert("RGBA")
    # 去掉方向信息
    im = ImageOps.exif_transpose(im)

    for action in params.actions:
        pass
