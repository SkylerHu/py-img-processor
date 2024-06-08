#!/usr/bin/env python
# coding=utf-8
import typing
import re

from py_enum import ChoiceEnum

from imgprocessor import enums, settings
from imgprocessor.exceptions import ParamValidateException, ParamParseException


class BaseParser(object):
    # 用来定义参数
    ARGS = {}

    @classmethod
    def validate(cls, **kwargs: typing.Any) -> dict:
        data = {}
        for key, config in cls.ARGS.items():
            _type = config["type"]
            _default = config.get("default")
            if key not in kwargs:
                # 配置的default仅当在没有传递值的时候才生效
                if _default is not None:
                    data[key] = _default
                continue
            value = kwargs.get(key)
            try:
                if _type == enums.ArgType.INTEGER:
                    value = cls._validate_int(value, **config)
                elif _type == enums.ArgType.STRING:
                    value = cls._validate_str(value, **config)
                elif _type == enums.ArgType.CHOICES:
                    value = cls._validate_choices(value, **config)
            except ParamValidateException as e:
                raise ParamValidateException(f"参数 {key}={value} 不符合要求：{e}")
            data[key] = value

        return data

    @classmethod
    def _validate_choices(
        cls, value: typing.Any, choices: typing.Optional[ChoiceEnum] = None, **kwargs: dict
    ) -> typing.Any:
        if choices is not None and value not in choices:
            raise ParamValidateException(f"枚举值只能是其中之一 {choices.values}")
        return value

    @classmethod
    def _validate_str(cls, value: typing.Any, regex: typing.Optional[str] = None, **kwargs: dict) -> str:
        if not isinstance(value, str):
            raise ParamValidateException("必须是字符串类型")
        if regex and not re.match(regex, value):
            raise ParamValidateException(f"不符合格式要求，需符合正则：{regex}")
        return value

    @classmethod
    def _validate_int(
        cls,
        value: typing.Any,
        min: typing.Optional[int] = None,
        max: typing.Optional[int] = None,
        **kwargs: dict,
    ) -> int:
        if isinstance(value, int):
            v = value
        elif isinstance(value, str):
            if not value.isdigit():
                raise ParamValidateException("必须是整数")
            v = int(value)
        else:
            raise ParamValidateException("必须是整数")
        if min is not None and v < min:
            raise
        if max is not None and v > max:
            raise

        return v

    @classmethod
    def parse_str(cls, key: str, param_str: str) -> dict:
        """将字符串参数转化为json格式数据

        Args:
            key: 参数类别，示例： `resize`
            param_str: 字符串参数，示例：`h_100,m_lfit`

        Raises:
            exceptions.ParseParamException: 解析参数不符合预期会抛出异常

        Returns:
            输出json格式参数，例如返回`{"key": "resize", "h": "100", "m": "lfit"}`
        """
        params = {}
        for item in param_str.split(","):
            if not item:
                continue
            info = item.split("_", 1)
            if len(info) != 2:
                raise ParamParseException(f"参数 {item} 不合法，参考 k_v 下划线隔开的格式")
            k, v = info
            params[k] = v

        params["key"] = key
        return params


class ResizeAction(BaseParser):

    ARGS = {
        "m": {"type": enums.ArgType.CHOICES, "default": enums.ResizeMode.LFIT, "choices": enums.ResizeMode},
        "w": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "h": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "l": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "s": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        "limit": {"type": enums.ArgType.INTEGER, "default": 1, "min": 0, "max": 1},
        "color": {"type": enums.ArgType.STRING, "default": "FFFFFF", "regex": "^#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$"},
        "p": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 1000},
    }

    def __init__(
        self,
        m: str = enums.ResizeMode.LFIT,
        w: int = 0,
        h: int = 0,
        l: int = 1,
        s: int = 1,
        limit: int = 1,
        color: str = "FFFFFF",
        p: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.key = enums.OpAction.RESIZE
        self.m = m
        self.w = w
        self.h = h
        self.l = l  # noqa: E741
        self.s = s
        self.limit = limit
        self.color = color
        self.p = p

    @classmethod
    def init(cls, data: dict) -> "ResizeAction":
        params = cls.validate(data)
        ins = cls(**params)
        return ins


__ACTION_PARASER_MAP = {
    enums.OpAction.RESIZE: ResizeAction,
}


class TransferConfig(object):
    """图片处理输入参数"""

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
        for i in actions:
            cls = __ACTION_PARASER_MAP.get(i.get("key"))
            if not cls:
                continue
            _actions.append(cls.init(i))
        self.actions = _actions

    @classmethod
    def parse_str(cls, value: str) -> "TransferConfig":
        """
        仅将字符串解析成json参数，不对参数合法性做校验

        Args:
            value: 输入参数，示例 crop,x_800,y_50/resize,h_100,m_lfit

        Returns:
            实例化TransferConfig

        """
        fmt = None
        quality = None
        actions = []

        for item in value.split("/"):
            info = item.split(",", 1)
            if not info:
                # 缺少key直接跳过
                continue
            if len(info) == 1:
                key = info[0]
                param_str = ""
            else:
                key, param_str = info

            # 解析具体参数
            if key not in enums.OpAction:
                continue
            if key == enums.OpAction.FORMAT:
                fmt = param_str
            elif key == enums.OpAction.QUALITY:
                if not param_str.isdigit():
                    raise ParamParseException("参数 quality 必须是正整数")
                quality = int(param_str)
            else:
                action = __ACTION_PARASER_MAP[key].parse_str(key, param_str)
                actions.append(action)

        json_data = {
            "format": fmt,
            "quality": quality,
            "actions": actions,
        }
        return cls(**json_data)
