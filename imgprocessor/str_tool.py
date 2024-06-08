#!/usr/bin/env python
# coding=utf-8
import typing
import base64


def is_number(s: str) -> bool:
    """
    判断字符串是否是数值

    Args:
        s: 输入字符串

    Returns:
        返回判断结果

    """
    if s.isdigit():
        # 只能判断正整数
        return True
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def str_to_number(s: str, is_raise: bool = False) -> typing.Union[int, float, str]:
    """
    字符串转化成数字

    Args:
        s: 输入字符串
        is_raise: 是否抛出异常

    Returns:
        输出数值

    """
    if s.isdigit():
        # 只能处理正整数
        return int(s)
    try:
        if "." in s:
            # 小数
            v = float(s)
        else:
            v = int(s)
    except ValueError as e:
        if is_raise:
            raise e
        v = s
    return v


def base64url_encode(value: str) -> str:
    """
    对内容进行URL安全的Base64编码，需要将结果中的部分编码替换：

    - 将结果中的加号 `+` 替换成短划线 `-`;
    - 将结果中的正斜线 `/` 替换成下划线 `_`;
    - 将结果中尾部的所有等号 `=` 省略。

    Args:
        value: 输入字符串

    Returns:
        返回编码后字符串

    """
    s = base64.urlsafe_b64encode(value.encode()).decode()
    s = s.strip("=")
    return s


def base64url_decode(value: str) -> str:
    """
    对URL安全编码进行解码

    Args:
        value: 输入编码字符串

    Returns:
        解码后字符串

    """
    # 补全后面等号
    padding = 4 - (len(value) % 4)
    value = value + ("=" * padding)
    # 解码
    s = base64.urlsafe_b64decode(value.encode()).decode()
    s = s.strip("=")
    return s
