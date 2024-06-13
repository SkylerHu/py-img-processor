#!/usr/bin/env python
# coding=utf-8
import typing

from imgprocessor import enums
from .base import BaseParser


class CropParser(BaseParser):

    key = enums.OpAction.CROP
    ARGS = {}

    def __init__(
        self,
        **kwargs: typing.Any,
    ) -> None:
        pass
