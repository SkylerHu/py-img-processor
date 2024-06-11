#!/usr/bin/env python
# coding=utf-8
import typing
import os
import tempfile

from PIL import Image, ImageOps

from imgprocessor import settings, enums, actions
from imgprocessor.exceptions import ProcessLimitException
from imgprocessor.params import BaseParser, ProcessParams


__ACTION_METHOD: dict = {
    enums.OpAction.RESIZE: actions.action_resize,
}


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
        method = __ACTION_METHOD.get(parser.key)
        if not callable(method):
            continue
        im = method(im, parser)

    return im


def save_img_to_file(
    im: Image,
    out_path: typing.Optional[str] = None,
    **kwargs: typing.Any,
) -> typing.Optional[typing.ByteString]:
    fmt = kwargs.get("format")

    if fmt != im.format:
        if fmt == enums.ImageFormat.JPEG:
            if im.mode != "RGB":
                im = im.convert("RGB")

    if not kwargs.get("quality"):
        if im.format == enums.ImageFormat.JPEG:
            kwargs["quality"] = "keep"
        else:
            kwargs["quality"] = settings.PROCESSOR_DEFAULT_QUALITY

    if out_path:
        # icc_profile 是为解决色域的问题
        im.save(out_path, **kwargs)
        return None

    # 没有传递保存的路径，返回文件内容
    with tempfile.TemporaryFile() as fp:
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

    kwargs = {"format": params.format or ori_im.format, "icc_profile": ori_im.info.get("icc_profile")}
    if params.quality:
        kwargs["quality"] = params.quality
    return save_img_to_file(im, out_path=out_path, **kwargs)
