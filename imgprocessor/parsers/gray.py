#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import ImageFile

from imgprocessor import enums
from .base import BaseParser


class GrayParser(BaseParser):

    KEY = enums.OpAction.GRAY.value
    ARGS = {}

    def __init__(
        self,
        **kwargs: typing.Any,
    ) -> None:
        pass

    def do_action(self, im: ImageFile.ImageFile) -> ImageFile.ImageFile:
        im = im.convert("L")
        return im
