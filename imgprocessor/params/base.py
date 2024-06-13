import typing
import re

from py_enum import ChoiceEnum

from imgprocessor import enums
from imgprocessor.exceptions import ParamValidateException, ParamParseException


class BaseParser(object):
    # 用来定义参数
    key: typing.Any = ""
    ARGS: dict = {}

    @classmethod
    def init(cls, data: dict) -> "BaseParser":
        params = cls.validate_args(**data)
        ins = cls(**params)
        ins.validate()
        return ins

    @classmethod
    def init_by_str(cls, param_str: str) -> "BaseParser":
        data = cls.parse_str(param_str)
        return cls.init(data)

    def validate(self) -> None:
        """由子类继承实现各类实例的数据校验"""
        pass

    @classmethod
    def validate_args(cls, **kwargs: typing.Any) -> dict:
        data = {}
        for key, config in cls.ARGS.items():
            _type = config["type"]
            _default = config.get("default")
            if key not in kwargs:
                # 配置的default仅当在没有传递值的时候才生效
                if _default is not None:
                    data[key] = _default
            else:
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
            raise ParamValidateException("参数类型不符合要求，必须是字符串类型")
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
                raise ParamValidateException("参数类型不符合要求，必须是整数")
            v = int(value)
        else:
            raise ParamValidateException("必须是整数")
        if min is not None and v < min:
            raise ParamValidateException(f"参数不在取值范围内，最小值为{min}")
        if max is not None and v > max:
            raise ParamValidateException(f"参数不在取值范围内，最大值为{max}")

        return v

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
        info = param_str.split(",")
        key = info[0]
        params = {}
        for item in info[1:]:
            if not item:
                continue
            info = item.split("_", 1)
            if len(info) != 2:
                raise ParamParseException(f"参数 {item} 不合法，参考 k_v 下划线隔开的格式")
            k, v = info
            params[k] = v

        params["key"] = key
        return params
