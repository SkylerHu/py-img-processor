#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import enums
from imgprocessor.exceptions import ParamValidateException

from .base import BaseParser  # noqa: F401
from .resize import ResizeParser
from .crop import CropParser


class ProcessParams(object):
    """图像处理输入参数"""

    __ACTION_PARASER_MAP: dict = {
        enums.OpAction.RESIZE: ResizeParser,
        enums.OpAction.CROP: CropParser,
    }

    def __init__(
        self,
        format: typing.Optional[str] = None,
        quality: typing.Optional[int] = None,
        actions: typing.Optional[list] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.format = format
        self.quality = quality
        _actions = []
        for i in actions or []:
            key = i.get("key")
            cls = self.__ACTION_PARASER_MAP.get(key)
            if not cls:
                continue
            _actions.append(cls.init(i))
        self.actions = _actions

    @classmethod
    def parse_str(cls, value: str) -> "ProcessParams":
        """
        仅将字符串解析成json参数，不对参数合法性做校验

        Args:
            value: 输入参数，示例 crop,x_800,y_50/resize,h_100,m_lfit

        Returns:
            实例化TransferConfig

        """
        fmt: typing.Optional[str] = None
        quality: typing.Optional[int] = None
        actions: list = []

        for item in value.split("/"):
            info = item.split(",", 1)
            if len(info) == 1:
                key = info[0]
                if not key:
                    continue
                param_str = ""
            else:
                key, param_str = info

            # 解析具体参数
            if key == enums.OpAction.FORMAT:  # type: ignore
                fmt_values = [v.lower() for v in enums.ImageFormat.values]
                if param_str not in fmt_values:
                    raise ParamValidateException(f"参数 format 只能是其中之一：{fmt_values}")
                fmt = param_str
            elif key == enums.OpAction.QUALITY:  # type: ignore
                if not param_str.isdigit():
                    raise ParamValidateException("参数 quality 必须是大于0的正整数")
                quality = int(param_str)
                if quality < 1 or quality > 100:
                    raise ParamValidateException("参数 quality 取值范围为[1, 100]")
            else:
                action_cls = cls.__ACTION_PARASER_MAP.get(key)
                if not action_cls:
                    continue
                action = action_cls.parse_str(item)
                actions.append(action)

        return cls(format=fmt, quality=quality, actions=actions)
