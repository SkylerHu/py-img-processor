#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import enums
from imgprocessor.exceptions import ParamParseException

from .base import BaseParser, ImgSaveParser
from .resize import ResizeParser
from .crop import CropParser
from .circle import CircleParser
from .blur import BlurParser
from .rotate import RotateParser
from .alpha import AlphaParser
from .gray import GrayParser
from .watermark import WatermarkParser
from .merge import MergeParser


_ACTION_PARASER_MAP: dict[str, typing.Any] = {
    enums.OpAction.RESIZE.value: ResizeParser,
    enums.OpAction.CROP.value: CropParser,
    enums.OpAction.CIRCLE.value: CircleParser,
    enums.OpAction.BLUR.value: BlurParser,
    enums.OpAction.ROTATE.value: RotateParser,
    enums.OpAction.ALPHA.value: AlphaParser,
    enums.OpAction.GRAY.value: GrayParser,
    enums.OpAction.WATERMARK.value: WatermarkParser,
    enums.OpAction.MERGE.value: MergeParser,
}


class ProcessParams(object):
    """图像处理输入参数"""

    @classmethod
    def init(cls, params: typing.Union["ProcessParams", dict, str]) -> "ProcessParams":
        if isinstance(params, ProcessParams):
            return params
        if isinstance(params, dict):
            return cls(**params)
        return cls.parse_str(params)

    def __init__(
        self,
        enable_base64: bool = False,
        actions: typing.Optional[list] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.save_parser: ImgSaveParser = ImgSaveParser.init(kwargs, enable_base64=enable_base64)  # type: ignore

        _actions: list[BaseParser] = []
        for i in actions or []:
            key = i.get("key")
            cls = _ACTION_PARASER_MAP.get(key)
            if not cls:
                continue
            _actions.append(cls.init(i, enable_base64=enable_base64))
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
        actions: list = []

        save_args = [""]  # 加空字符串，是为了保证解析出key

        save_keys = list(ImgSaveParser.ARGS.keys())
        for item in value.split("/"):
            if not item:
                continue
            info = item.split(",", 1)
            if len(info) == 1:
                key = info[0]
                param_str = ""
            else:
                key, param_str = info
            if not key:
                raise ParamParseException(f"参数必须指定操作类型 [{item}]不符合参数要求")
            if key in save_keys:
                save_args.append(f"{key}_{param_str}")
            else:
                action_cls = _ACTION_PARASER_MAP.get(key)
                if not action_cls:
                    continue
                action = action_cls.parse_str(item)
                actions.append(action)

        kwargs = ImgSaveParser.parse_str(",".join(save_args))
        return cls(enable_base64=True, actions=actions, **kwargs)
