#!/usr/bin/env python
# coding=utf-8
import typing

import os
import re
import tempfile
import urllib.parse
from urllib.request import urlretrieve

from PIL import Image, ImageOps

from imgprocessor import settings, enums, utils
from imgprocessor.exceptions import ParamValidateException, ParamParseException, ProcessLimitException


_ALLOW_SCHEMES = ("http", "https")


class BaseParser(object):
    # 用来定义参数
    KEY: typing.Any = ""
    ARGS: dict = {}

    def __init__(self, **kwargs: typing.Any) -> None:
        pass

    @classmethod
    def init(cls, data: dict, enable_base64: bool = False) -> "BaseParser":
        params = cls.validate_args(enable_base64=enable_base64, **data)
        ins = cls(**params)
        ins.validate()
        return ins

    @classmethod
    def init_by_str(cls, param_str: str) -> "BaseParser":
        data = cls.parse_str(param_str)
        return cls.init(data, enable_base64=True)

    def validate(self) -> None:
        """由子类继承实现各类实例的数据校验"""
        pass

    def do_action(self, im: Image) -> Image:
        raise NotImplementedError

    def to_dict(self) -> dict:
        data = {}
        for k in self.ARGS.keys():
            if k in self.__dict__:
                data[k] = self.__dict__.get(k)
        return data

    @classmethod
    def validate_args(cls, enable_base64: bool = False, **kwargs: typing.Any) -> dict:
        data = {}
        for key, config in cls.ARGS.items():
            _type = config["type"]
            _default = config.get("default")
            if key not in kwargs:
                required = config.get("required")
                if required:
                    raise ParamValidateException(f"缺少必要参数{key}")
                # 配置的default仅当在没有传递值的时候才生效
                if _default is not None:
                    data[key] = _default
            else:
                value = kwargs.get(key)
                try:
                    if _type == enums.ArgType.INTEGER:
                        value = cls._validate_number(value, **config)
                    elif _type == enums.ArgType.FLOAT:
                        value = cls._validate_number(value, use_float=True, **config)
                    elif _type == enums.ArgType.STRING:
                        value = cls._validate_str(value, enable_base64=enable_base64, **config)
                    elif _type == enums.ArgType.URI:
                        value = cls._validate_uri(value, enable_base64=enable_base64, **config)
                    elif _type == enums.ArgType.ACTION:
                        if value and isinstance(value, str):
                            value = cls._validate_str(value, enable_base64=enable_base64, **config)

                    choices = config.get("choices")
                    if choices and value not in choices:
                        raise ParamValidateException(f"{key}枚举值只能是其中之一 {choices.values}")
                except ParamValidateException as e:
                    raise ParamValidateException(f"参数 {key}={value} 不符合要求：{e}")
                data[key] = value

        return data

    @classmethod
    def _validate_str(
        cls,
        value: typing.Any,
        enable_base64: bool = False,
        regex: typing.Optional[str] = None,
        base64_encode: bool = False,
        max_length: typing.Optional[int] = None,
        **kwargs: typing.Any,
    ) -> str:
        if not isinstance(value, str):
            raise ParamValidateException("参数类型不符合要求，必须是字符串类型")
        if enable_base64 and base64_encode:
            value = utils.base64url_decode(value)
        if max_length is not None and len(value) > max_length:
            raise ParamValidateException(f"长度不允许超过{max_length}个字符")
        if regex and not re.match(regex, value):
            raise ParamValidateException(f"不符合格式要求，需符合正则：{regex}")
        return value

    @classmethod
    def _validate_number(
        cls,
        value: typing.Any,
        min: typing.Optional[int] = None,
        max: typing.Optional[int] = None,
        use_float: bool = False,
        **kwargs: typing.Any,
    ) -> typing.Union[int, float]:
        if isinstance(value, int) or (use_float and isinstance(value, (int, float))):
            v = value
        elif isinstance(value, str):
            if not value.isdigit():
                if use_float:
                    try:
                        v = float(value)
                    except Exception:
                        raise ParamValidateException("参数类型不符合要求，必须是数值")
                else:
                    raise ParamValidateException("参数类型不符合要求，必须是整数")
            else:
                v = int(value)
        else:
            raise ParamValidateException("必须是整数")
        if min is not None and v < min:
            raise ParamValidateException(f"参数不在取值范围内，最小值为{min}")
        if max is not None and v > max:
            raise ParamValidateException(f"参数不在取值范围内，最大值为{max}")

        return v

    @classmethod
    def _validate_uri(cls, value: typing.Any, **kwargs: typing.Any) -> str:
        """校验输入的资源，转换为本地绝对路径

        Args:
            value: 输入值
            workspace: 限制资源路径，可传递空字符串忽略校验. Defaults to None.
            allow_domains: 限制资源地址的域名，可传递空数组忽略校验. Defaults to None.

        Raises:
            ParamValidateException: 参数校验异常

        Returns:
            系统文件绝对路径
        """
        # 首先是字符串
        value = cls._validate_str(value, **kwargs)
        ori_value = value
        # 判断是否是链接
        parsed_url = urllib.parse.urlparse(value)
        if parsed_url.scheme not in _ALLOW_SCHEMES:
            value = os.path.realpath(os.fspath(value))
            if not os.path.isfile(value):
                raise ParamValidateException(f"系统文件不存在: {ori_value}")

            workspaces: tuple = settings.PROCESSOR_WORKSPACES or ()
            _workspace = [os.path.realpath(os.fspath(ws)) for ws in workspaces]
            if _workspace and not value.startswith(tuple(_workspace)):
                raise ParamValidateException(f"文件必须在 PROCESSOR_WORKSPACES={workspaces} 目录下: {ori_value}")
        else:
            # 是链接地址
            domain = parsed_url.netloc
            if not domain:
                raise ParamValidateException(f"链接未解析出域名: {ori_value}")
            allow_domains = settings.PROCESSOR_ALLOW_DOMAINS
            if allow_domains and not parsed_url.netloc.endswith(tuple(allow_domains)):
                raise ParamValidateException(
                    f"域名不合法, {parsed_url.netloc} 不在 {allow_domains} 范围内: {ori_value}"
                )
        return value

    @classmethod
    def parse_str(cls, param_str: str) -> dict:
        """将字符串参数转化为json格式数据

        Args:
            param_str: 字符串参数，示例：`resize,h_100,m_lfit`

        Raises:
            exceptions.ParseParamException: 解析参数不符合预期会抛出异常

        Returns:
            输出json格式参数，例如返回`{"key": "resize", "h": "100", "m": "lfit"}`
        """
        params = {}
        info = param_str.split(",")
        key = info[0]
        if key != cls.KEY:
            raise ParamParseException(f"解析出来的key={key}与{cls.__name__}.KEY={cls.KEY}不匹配")
        for item in info[1:]:
            info = item.split("_", 1)
            if len(info) == 2:
                k, v = info
                params[k] = v
            else:
                params["value"] = info[0]

        params["key"] = key
        return params


def pre_processing(im: Image, use_alpha: bool = False) -> Image:
    """预处理图像，默认转成`RGB`，若为`use_alpha=True`转为`RGBA`

    Args:
        im: 输入图像
        use_alpha: 是否处理透明度

    Returns:
        输出图像
    """
    # 去掉方向信息
    orientation = im.getexif().get(0x0112)
    if orientation and 2 <= orientation <= 8:
        im = ImageOps.exif_transpose(im)

    if im.mode not in ["RGB", "RGBA"]:
        # 统一处理成RGBA进行操作:
        # 1. 像rotate/resize操作需要RGB模式；
        # 2. 像水印操作需要RGBA；
        im = im.convert("RGBA")

    if use_alpha and im.mode != "RGBA":
        im = im.convert("RGBA")

    return im


def compute_by_geography(
    src_w: int, src_h: int, x: int, y: int, w: int, h: int, g: typing.Optional[str], pf: str
) -> tuple[int, int]:
    """计算 大小(w,h)的图像相对于(src_w, src_h)图像的原点(x,y)位置"""
    if g == enums.Geography.NW:
        x, y = 0, 0
    elif g == enums.Geography.NORTH:
        x, y = int(src_w / 2 - w / 2), 0
    elif g == enums.Geography.NE:
        x, y = src_w - w, 0
    elif g == enums.Geography.WEST:
        x, y = 0, int(src_h / 2 - h / 2)
    elif g == enums.Geography.CENTER:
        x, y = int(src_w / 2 - w / 2), int(src_h / 2 - h / 2)
    elif g == enums.Geography.EAST:
        x, y = src_w - w, int(src_h / 2 - h / 2)
    elif g == enums.Geography.SW:
        x, y = 0, src_h - h
    elif g == enums.Geography.SOUTH:
        x, y = int(src_w / 2 - w / 2), src_h - h
    elif g == enums.Geography.SE:
        x, y = src_w - w, src_h - h
    elif pf:
        if "x" in pf:
            if x < 0 or x > 100:
                raise ParamValidateException(f"pf={pf}包含了x，所以x作为百分比取值范围为[0,100]")
            x = round(src_w * x / 100)
        if "y" in pf:
            if y < 0 or y > 100:
                raise ParamValidateException(f"pf={pf}包含了y，所以y作为百分比取值范围为[0,100]")
            y = round(src_h * y / 100)
    return x, y


def compute_by_ratio(src_w: int, src_h: int, ratio: str) -> tuple[int, int]:
    """根据输入宽高，按照比例比计算出最大区域

    Args:
        src_w: 输入宽度
        src_h: 输入高度
        ratio: 比例字符串，eg "4:3"

    Returns:
        计算后的宽高
    """
    w_r, h_r = ratio.split(":")
    wr, hr = int(w_r), int(h_r)
    if src_w * hr > src_h * wr:
        # 相对于目标比例，宽长了
        w = round(src_h * wr / hr)
        h = src_h
    elif src_w * hr < src_h * wr:
        w = src_w
        h = round(src_w * hr / wr)
    else:
        # 刚好符合比例
        w, h = src_w, src_h
    return w, h


def compute_splice_two_im(
    w1: int,
    h1: int,
    w2: int,
    h2: int,
    align: int = enums.PositionAlign.VERTIAL_CENTER,  # type: ignore
    order: int = enums.PositionOrder.BEFORE,  # type: ignore
    interval: int = 0,
) -> tuple:
    """拼接2个图像，计算整体大小和元素原点位置；数值单位都是像素

    Args:
        w1: 第1个元素的宽
        h1: 第1个元素的高
        w2: 第2个元素的宽
        h2: 第2个元素的高
        align: 对齐方式  see enums.PositionAlign
        order: 排序 see enums.PositionOrder
        interval: 元素之间的间隔

    Returns:
        整体占位w宽度
        整体占位y宽度
        第1个元素的原点位置x1
        第1个元素的原点位置y1
        第2个元素的原点位置x2
        第2个元素的原点位置y2
    """
    if align in [enums.PositionAlign.TOP, enums.PositionAlign.HORIZONTAL_CENTER, enums.PositionAlign.BOTTOM]:
        # 水平顺序
        # 计算整体占位大小w,h
        w, h = w1 + w2 + interval, max(h1, h2)

        if align == enums.PositionAlign.TOP:
            y1, y2 = 0, 0
        elif align == enums.PositionAlign.BOTTOM:
            y1, y2 = h - h1, h - h2
        else:
            y1, y2 = int((h - h1) / 2), int((h - h2) / 2)

        if order == enums.PositionOrder.BEFORE:
            x1, x2 = 0, w1 + interval
        else:
            x1, x2 = w2 + interval, 0
    else:
        # 垂直
        w, h = max(w1, w2), h1 + h2 + interval
        if align == enums.PositionAlign.LEFT:
            x1, x2 = 0, 0
        elif align == enums.PositionAlign.RIGHT:
            x1, x2 = w - w1, w - w2
        else:
            x1, x2 = int((w - w1) / 2), int((w - w2) / 2)

        if order == enums.PositionOrder.BEFORE:
            y1, y2 = 0, h1 + interval
        else:
            y1, y2 = h2 + interval, 0

    return w, h, x1, y1, x2, y2


def validate_ori_im(ori_im: Image) -> None:
    src_w, src_h = ori_im.size
    if src_w > settings.PROCESSOR_MAX_W_H or src_h > settings.PROCESSOR_MAX_W_H:
        raise ProcessLimitException(
            f"图像宽和高单边像素不能超过{settings.PROCESSOR_MAX_W_H}像素，输入图像({src_w}, {src_h})"
        )
    if src_w * src_h > settings.PROCESSOR_MAX_PIXEL:
        raise ProcessLimitException(f"图像总像素不可超过{settings.PROCESSOR_MAX_PIXEL}像素，输入图像({src_w}, {src_h})")


def trans_uri_to_im(uri: str) -> Image:
    """将输入资源转换成Image对象

    Args:
        uri: 文件路径 或者 可下载的链接地址

    Raises:
        ProcessLimitException: 处理图像大小/像素限制

    Returns:
        Image对象
    """
    parsed_url = urllib.parse.urlparse(uri)
    if parsed_url.scheme in _ALLOW_SCHEMES:
        with tempfile.NamedTemporaryFile() as fp:
            # 输入值计算md5作为文件名；重复地址本地若存在不下载多次
            urlretrieve(uri, filename=fp.name)
            fp.seek(0)

            size = os.path.getsize(fp.name)
            if size > settings.PROCESSOR_MAX_FILE_SIZE * 1024 * 1024:
                raise ProcessLimitException(f"图像文件大小不得超过{settings.PROCESSOR_MAX_FILE_SIZE}MB")

            ori_im = Image.open(fp)
            validate_ori_im(ori_im)
            # 解决临时文件close后im对象不能正常使用得问题
            ori_im = ori_im.copy()
    else:
        size = os.path.getsize(uri)
        if size > settings.PROCESSOR_MAX_FILE_SIZE * 1024 * 1024:
            raise ProcessLimitException(f"图像文件大小不得超过{settings.PROCESSOR_MAX_FILE_SIZE}MB")
        ori_im = Image.open(uri)
        validate_ori_im(ori_im)

    return ori_im


class ImgSaveParser(BaseParser):
    KEY = ""
    ARGS = {
        "format": {"type": enums.ArgType.STRING, "default": None},
        "quality": {"type": enums.ArgType.INTEGER, "default": None, "min": 1, "max": 100},
        # 1 表示将原图设置成渐进显示
        "interlace": {"type": enums.ArgType.INTEGER, "default": 0, "choices": [0, 1]},
    }

    def __init__(
        self,
        format: typing.Optional[str] = None,
        quality: typing.Optional[int] = None,
        interlace: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.format = format
        self.quality = quality
        self.interlace = interlace

    def validate(self) -> None:
        super().validate()
        if self.format:
            fmt_values = [v.lower() for v in enums.ImageFormat.values]
            if self.format not in fmt_values:
                raise ParamValidateException(f"参数 format 只能是其中之一：{fmt_values}")

    def compute(self, in_im: Image, out_im: Image) -> dict:
        kwargs = {
            "format": self.format or in_im.format,
            # png 和 gif 格式的选项是 interlace（一般翻译成交错），jpeg(jpg) 的选项则是 progressive （翻译成 渐进）
            "progressive": True if self.interlace else False,
            "interlace": self.interlace,
        }
        # 为了解决色域问题
        icc_profile = in_im.info.get("icc_profile")
        if icc_profile:
            kwargs["icc_profile"] = icc_profile
        if self.quality:
            kwargs["quality"] = self.quality
        return kwargs
