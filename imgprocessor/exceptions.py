#!/usr/bin/env python
# coding=utf-8

class ProcessException(Exception):
    pass


class ParamParseException(ProcessException):
    pass


class ParamValidateException(ProcessException):
    pass
