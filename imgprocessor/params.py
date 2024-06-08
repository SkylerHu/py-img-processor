#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import exceptions, enums, str_tool


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
        self.actions = actions or []

    @classmethod
    def _parse(cls, key: str, param_str: str) -> dict:
        """将字符串参数转化为json格式数据，示例：resize,h_100,m_lfit

        Args:
            key: 参数类别，示例中的`resize`
            param_str: 字符串参数，示例中的`h_100,m_lfit`

        Raises:
            exceptions.ParseParamException: 解析参数不符合预期会抛出异常

        Returns:
            输出json格式参数
        """
        params = {}
        for item in param_str.split(","):
            if not item:
                continue
            info = item.split("_", 1)
            if len(info) != 2:
                raise exceptions.ParamParseException(f"参数 {item} 不合法，参考 k_v 下划线隔开的格式")
            k, v = info
            v = str_tool.str_to_number(v)
            params[k] = v

        params["action"] = key
        return params

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
                    raise exceptions.ParamParseException("参数 quality 必须是正整数")
                quality = int(param_str)
            else:
                action = cls._parse(key, param_str)
                actions.append(action)

        json_data = {
            "format": fmt,
            "quality": quality,
            "actions": actions,
        }
        return cls(**json_data)


def __ratio_to_wh(ow, oh, ratio):
    w_r, h_r = ratio.split(":")
    w_r, h_r = int(w_r), int(h_r)  # 仅支持整数
    if ow * h_r > oh * w_r:
        # 相对于目标比例，宽长了
        w = int(oh * w_r / h_r)
        h = oh
    elif ow * h_r < oh * w_r:
        w = ow
        h = int(ow * h_r / w_r)
    else:
        # 搞好符合比例
        w, h = ow, oh
    return w, h

