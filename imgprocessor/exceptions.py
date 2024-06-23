#!/usr/bin/env python
# coding=utf-8


class ProcessException(Exception):
    """图像处理异常基类"""

    pass


class ProcessLimitException(Exception):
    """图像处理限制"""

    pass


class ParamParseException(ProcessException):
    """解析参数出现错误"""

    pass


class ParamValidateException(ProcessException):
    """对参数进行校验"""

    pass
