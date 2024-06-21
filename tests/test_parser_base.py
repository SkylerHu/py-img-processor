#!/usr/bin/env python
# coding=utf-8
import pytest

from PIL import Image

from imgprocessor import enums, settings
from imgprocessor.parsers import base as parser_base
from imgprocessor.exceptions import ParamValidateException, ParamParseException


def test_args_config() -> None:
    class TestParser(parser_base.BaseParser):
        KEY = enums.OpAction.RESIZE
        ARGS = {
            "m": {"type": enums.ArgType.STRING, "default": None, "choices": enums.ResizeMode},
            "w": {"type": "xxx", "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
            "h": {"type": enums.ArgType.FLOAT, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
            "x": {"type": enums.ArgType.INTEGER, "required": True, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
            "t": {"type": enums.ArgType.STRING, "max_length": 2},
        }

    data = TestParser.validate_args(w="a", h2=2, x=1)
    assert data.get("w") == "a"
    assert data.get("h") == 0
    assert "m" not in data, "default is None默认不赋值"

    data = TestParser.parse_str("resize,h_1.5,x_1")
    assert sorted(data.keys()) == sorted(["key", "x", "h"])

    with pytest.raises(ParamValidateException, match="缺少必要参数"):
        TestParser.init_by_str("resize,h_1.5")

    with pytest.raises(ParamValidateException, match="长度不允许超过"):
        TestParser.init_by_str("resize,x_1,t_test")

    with pytest.raises(ParamValidateException, match="参数类型不符合要求"):
        TestParser.init_by_str("resize,x_1,h_test")

    with pytest.raises(ParamParseException, match="解析出来的key.*不匹配"):
        TestParser.init_by_str("corp,x_1,h_test")

    with pytest.raises(NotImplementedError):
        TestParser().do_action(None)


@pytest.mark.parametrize(
    "params,expected",
    [
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.TOP, enums.PositionOrder.BEFORE, 0),
            (3840, 1080, 0, 0, 1920, 0),
        ),
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.TOP, enums.PositionOrder.AFTER, 0),
            (3840, 1080, 1920, 0, 0, 0),
        ),
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.LEFT, enums.PositionOrder.BEFORE, 0),
            (1920, 2160, 0, 0, 0, 1080),
        ),
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.RIGHT, enums.PositionOrder.AFTER, 0),
            (1920, 2160, 0, 1080, 0, 0),
        ),
        (
            (1920, 1080, 1280, 720, enums.PositionAlign.VERTIAL_CENTER, enums.PositionOrder.AFTER, 0),
            (1920, 1800, 0, 720, 320, 0),
        ),
    ],
)
def test_splice_two_im(params: tuple, expected: tuple) -> None:
    # w1, h1, w2, h2, align, order, interval = params
    output = parser_base.compute_splice_two_im(*params)
    assert output == expected


@pytest.mark.usefixtures("clean_dir")
def test_pre_processing(img_rotate_90_with_exif: Image) -> None:
    assert img_rotate_90_with_exif.getexif().get(0x0112) > 0
    im = parser_base.pre_processing(img_rotate_90_with_exif)
    assert im.getexif().get(0x0112) is None
