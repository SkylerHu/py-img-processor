#!/usr/bin/env python
# coding=utf-8
import typing
import os
import tempfile
import colorsys

from PIL import Image, ImageOps

from imgprocessor import settings, enums
from imgprocessor.exceptions import ProcessLimitException
from imgprocessor.parsers import BaseParser, ProcessParams


def handle_img_actions(ori_im: Image, actions: list[BaseParser]) -> Image:
    src_w, src_h = ori_im.size
    if src_w > settings.PROCESSOR_MAX_W_H or src_h > settings.PROCESSOR_MAX_W_H:
        raise ProcessLimitException(
            f"图像宽和高单边像素不能超过{settings.PROCESSOR_MAX_W_H}像素，输入图像({src_w}, {src_h})"
        )
    if src_w * src_h > settings.PROCESSOR_MAX_PIXEL:
        raise ProcessLimitException(f"图像总像素不可超过{settings.PROCESSOR_MAX_PIXEL}像素，输入图像({src_w}, {src_h})")

    im = ori_im
    im = ImageOps.exif_transpose(im)

    for parser in actions:
        im = parser.do_action(im)

    return im


def save_img_to_file(
    im: Image,
    out_path: typing.Optional[str] = None,
    **kwargs: typing.Any,
) -> typing.Optional[typing.ByteString]:
    fmt = kwargs.get("format") or im.format
    kwargs["format"] = fmt

    if fmt.upper() == enums.ImageFormat.JPEG and im.mode == "RGBA":
        im = im.convert("RGB")

    if not kwargs.get("quality"):
        if fmt.upper() == enums.ImageFormat.JPEG and im.format == enums.ImageFormat.JPEG:
            kwargs["quality"] = "keep"
        else:
            kwargs["quality"] = settings.PROCESSOR_DEFAULT_QUALITY

    if out_path:
        # icc_profile 是为解决色域的问题
        im.save(out_path, **kwargs)
        return None

    # 没有传递保存的路径，返回文件内容
    suffix = fmt or "png"
    with tempfile.NamedTemporaryFile(suffix=f".{suffix}") as fp:
        im.save(fp.name, **kwargs)
        fp.seek(0)
        content = fp.read()
    return content


def process_image_by_path(
    input_path: str, out_path: str, params: typing.Union[ProcessParams, dict, str]
) -> typing.Optional[typing.ByteString]:
    size = os.path.getsize(input_path)
    if size > settings.PROCESSOR_MAX_FILE_SIZE * 1024 * 1024:
        raise ProcessLimitException(f"图像文件大小不得超过{settings.PROCESSOR_MAX_FILE_SIZE}MB")
    if isinstance(params, dict):
        params = ProcessParams(**params)
    elif isinstance(params, str):
        params = ProcessParams.parse_str(params)
    params = typing.cast(ProcessParams, params)

    ori_im = Image.open(input_path)
    # 处理图像
    im = handle_img_actions(ori_im, params.actions)

    kwargs = params.save_parser.compute(ori_im, im)
    return save_img_to_file(im, out_path=out_path, **kwargs)


def extract_main_color(img_path: str, delta_h: float = 0.3) -> str:
    """获取图像主色调

    Args:
        img_path: 输入图像的路径
        delta_h: 像素色相和平均色相做减法的绝对值小于改值，才用于计算主色调，取值范围[0,1]
    Returns:
        颜色值，eg: FFFFFF
    """
    r, g, b = 0, 0, 0
    im = Image.open(img_path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    # 转换成HSV即 色相(Hue)、饱和度(Saturation)、明度(alue)，取值范围[0,1]
    # 取H计算平均色相
    all_h = [colorsys.rgb_to_hsv(*im.getpixel((x, y)))[0] for x in range(im.size[0]) for y in range(im.size[1])]
    avg_h = sum(all_h) / (im.size[0] * im.size[1])
    # 取与平均色相相近的像素色值rgb用于计算，像素值取值范围[0,255]
    beyond = list(
        filter(
            lambda x: abs(colorsys.rgb_to_hsv(*x)[0] - avg_h) < delta_h,
            [im.getpixel((x, y)) for x in range(im.size[0]) for y in range(im.size[1])],
        )
    )
    if len(beyond):
        r = int(sum(e[0] for e in beyond) / len(beyond))
        g = int(sum(e[1] for e in beyond) / len(beyond))
        b = int(sum(e[2] for e in beyond) / len(beyond))

    color = "{}{}{}".format(hex(r)[2:].zfill(2), hex(g)[2:].zfill(2), hex(b)[2:].zfill(2))
    return color.upper()
