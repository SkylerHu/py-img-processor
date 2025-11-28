#!/usr/bin/env python
# coding=utf-8
import typing
import tempfile
import colorsys

from PIL import Image, ImageOps

from imgprocessor import enums, settings
from imgprocessor.parsers import BaseParser, ProcessParams
from imgprocessor.parsers.base import trans_uri_to_im


class ProcessorCtr(object):

    @classmethod
    def handle_img_actions(cls, ori_im: Image, actions: list[BaseParser]) -> Image:
        im = ori_im
        # 解决旋转问题
        im = ImageOps.exif_transpose(im)
        for parser in actions:
            im = parser.do_action(im)
        return im

    @classmethod
    def save_img_to_file(
        cls,
        im: Image,
        out_path: typing.Optional[str] = None,
        **kwargs: typing.Any,
    ) -> typing.Optional[typing.ByteString]:
        fmt = kwargs.get("format") or im.format

        if fmt and fmt.upper() == enums.ImageFormat.JPEG.value and im.mode == "RGBA":
            im = im.convert("RGB")

        if not kwargs.get("quality"):
            if fmt and fmt.upper() == enums.ImageFormat.JPEG.value and im.format == enums.ImageFormat.JPEG.value:
                kwargs["quality"] = "keep"
            else:
                kwargs["quality"] = settings.PROCESSOR_DEFAULT_QUALITY

        if out_path:
            # icc_profile 是为解决色域的问题
            im.save(out_path, **kwargs)
            return None

        # 没有传递保存的路径，返回文件内容
        suffix = fmt or "png"
        with tempfile.NamedTemporaryFile(suffix=f".{suffix}", dir=settings.PROCESSOR_TEMP_DIR) as fp:
            im.save(fp.name, **kwargs)
            fp.seek(0)
            content = fp.read()
        return content


def process_image(
    input_uri: str,
    params: typing.Union[ProcessParams, dict, str],
    out_path: typing.Optional[str] = None,
    **kwargs: typing.Any,
) -> typing.Optional[typing.ByteString]:
    """处理图像

    Args:
        input_uri: 输入图像路径
        params: 图像处理参数
        out_path: 输出图像保存路径

    Raises:
        ProcessLimitException: 超过处理限制会抛出异常

    Returns:
        默认输出直接存储无返回，仅当out_path为空时会返回处理后图像的二进制内容
    """
    # 初始化输入
    params_obj: ProcessParams = ProcessParams.init(params)
    with trans_uri_to_im(input_uri) as ori_im:
        # 处理图像
        im = ProcessorCtr.handle_img_actions(ori_im, params_obj.actions)
        # 输出、保存
        _kwargs = params_obj.save_parser.compute(ori_im, im)
        _kwargs.update(kwargs)
        ret = ProcessorCtr.save_img_to_file(im, out_path=out_path, **_kwargs)
    return ret


def process_image_obj(
    ori_im: Image,
    params: typing.Union[ProcessParams, dict, str],
    out_path: typing.Optional[str] = None,
    **kwargs: typing.Any,
) -> typing.Optional[typing.ByteString]:
    """处理图像

    Args:
        ori_im: 输入图像为Image对象
        params: 图像处理参数
        out_path: 输出图像保存路径

    Returns:
        默认输出直接存储无返回，仅当out_path为空时会返回处理后图像的二进制内容
    """
    params_obj: ProcessParams = ProcessParams.init(params)
    im = ProcessorCtr.handle_img_actions(ori_im, params_obj.actions)
    _kwargs = params_obj.save_parser.compute(ori_im, im)
    _kwargs.update(kwargs)
    ret = ProcessorCtr.save_img_to_file(im, out_path=out_path, **_kwargs)
    return ret


def extract_main_color(img_path: str, delta_h: float = 0.3) -> str:
    """获取图像主色调

    Args:
        img_path: 输入图像的路径
        delta_h: 像素色相和平均色相做减法的绝对值小于该值，才用于计算主色调，取值范围[0,1]

    Returns:
        颜色值，eg: FFFFFF
    """
    r, g, b = 0, 0, 0
    with Image.open(img_path) as im:
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
