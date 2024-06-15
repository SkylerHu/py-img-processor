#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import enums

from .base import BaseParser, ImgSaveParser  # noqa: F401
from .resize import ResizeParser
from .crop import CropParser
from .circle import CircleParser
from .blur import BlurParser
from .rotate import RotateParser
from .alpha import AlphaParser
from .gray import GrayParser
from .watermark import WatermarkParser


_ACTION_PARASER_MAP: dict[str, BaseParser] = {
    enums.OpAction.RESIZE: ResizeParser,  # type: ignore
    enums.OpAction.CROP: CropParser,  # type: ignore
    enums.OpAction.CIRCLE: CircleParser,  # type: ignore
    enums.OpAction.BLUR: BlurParser,  # type: ignore
    enums.OpAction.ROTATE: RotateParser,  # type: ignore
    enums.OpAction.ALPHA: AlphaParser,  # type: ignore
    enums.OpAction.GRAY: GrayParser,  # type: ignore
    enums.OpAction.WATERMARK: WatermarkParser,  # type: ignore
}


class ProcessParams(object):
    """图像处理输入参数"""

    def __init__(
        self,
        actions: typing.Optional[list] = None,
        **kwargs: typing.Any,
    ) -> None:
        self.save_parser: ImgSaveParser = ImgSaveParser.init(kwargs)

        _actions = []
        for i in actions or []:
            key = i.get("key")
            cls = _ACTION_PARASER_MAP.get(key)
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
        actions: list = []

        save_args = [""]  # 加空字符串，是为了保证解析出key

        for item in value.split("/"):
            if not item:
                continue
            info = item.split(",", 1)
            if len(info) == 1:
                key = info[0]
                if not key:
                    continue
                param_str = ""
            else:
                key, param_str = info

            if key in [enums.OpAction.FORMAT, enums.OpAction.QUALITY, enums.OpAction.INTERLACE]:
                save_args.append(f"{key}_{param_str}")
            else:
                action_cls = _ACTION_PARASER_MAP.get(key)
                if not action_cls:
                    continue
                action = action_cls.parse_str(item)
                actions.append(action)

        kwargs = ImgSaveParser.parse_str(",".join(save_args))
        return cls(actions=actions, **kwargs)
