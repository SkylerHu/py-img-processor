#!/usr/bin/env python
# coding=utf-8
import base64
import PIL

try:
    # python3.12之后被移除
    from distutils.version import StrictVersion as Version
except Exception:
    from packaging.version import Version  # type: ignore[no-redef]


def get_pil_version() -> Version:
    return Version(PIL.__version__)


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
