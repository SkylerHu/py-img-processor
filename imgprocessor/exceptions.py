#!/usr/bin/env python
# coding=utf-8


class ProcessException(Exception):
    pass


class ParamParseException(ProcessException):
    """解析参数出现错误"""

    pass


class ParamValidateException(ProcessException):
    """对参数进行校验"""

    pass
