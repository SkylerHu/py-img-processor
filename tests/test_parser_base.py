#!/usr/bin/env python
# coding=utf-8
import typing
import pytest

from PIL import Image

from imgprocessor import enums, settings
from imgprocessor.parsers import base as parser_base, ProcessParams
from imgprocessor.exceptions import ParamValidateException, ParamParseException


def test_args_config() -> None:
    class TestParser(parser_base.BaseParser):
        KEY = enums.OpAction.RESIZE.value
        ARGS = {
            "m": {"type": enums.ArgType.STRING.value, "default": None, "choices": enums.ResizeMode},
            "w": {"type": "xxx", "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
            "h": {"type": enums.ArgType.FLOAT.value, "default": 0, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
            "x": {"type": enums.ArgType.INTEGER.value, "required": True, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
            "t": {"type": enums.ArgType.STRING.value, "max_length": 2},
        }

        def __init__(self, x: typing.Optional[int] = None, **kwargs: typing.Any) -> None:
            super().__init__(**kwargs)
            self.x = x

    data = TestParser.validate_args(w="a", h2=2, x=1)
    assert data.get("w") == "a"
    assert data.get("h") == 0
    assert "m" not in data, "default is None默认不赋值"

    data = TestParser.parse_str("resize,h_1.5,x_1")
    assert sorted(data.keys()) == sorted(["key", "x", "h"])

    p = TestParser.init_by_str("resize,h_1.5,x_1")
    assert p.to_dict() == {"x": 1}

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
            (1920, 1080, 1920, 1080, enums.PositionAlign.TOP.value, enums.PositionOrder.BEFORE.value, 0),
            (3840, 1080, 0, 0, 1920, 0),
        ),
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.TOP.value, enums.PositionOrder.AFTER.value, 0),
            (3840, 1080, 1920, 0, 0, 0),
        ),
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.LEFT.value, enums.PositionOrder.BEFORE.value, 0),
            (1920, 2160, 0, 0, 0, 1080),
        ),
        (
            (1920, 1080, 1920, 1080, enums.PositionAlign.RIGHT.value, enums.PositionOrder.AFTER.value, 0),
            (1920, 2160, 0, 1080, 0, 0),
        ),
        (
            (1920, 1080, 1280, 720, enums.PositionAlign.VERTIAL_CENTER.value, enums.PositionOrder.AFTER.value, 0),
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


@pytest.mark.usefixtures("clean_dir")
def test_transpose_im_fallback(img_rotate_90_with_exif: Image, monkeypatch) -> None:
    """exif_transpose 抛出异常时，回退到手动读取 Orientation 进行转置"""
    from PIL import ImageOps

    orig_size = img_rotate_90_with_exif.size
    orientation = img_rotate_90_with_exif.getexif().get(0x0112)
    assert orientation is not None and orientation > 1

    def mock_exif_transpose(im, **kwargs):
        raise OSError(-2, "corrupted EXIF data")

    monkeypatch.setattr(ImageOps, "exif_transpose", mock_exif_transpose)
    im = parser_base.transpose_im(img_rotate_90_with_exif)
    assert im.size == (orig_size[1], orig_size[0])


def test_transpose_im_fallback_without_orientation(monkeypatch) -> None:
    """exif_transpose 抛出异常且无可用 Orientation 时，保持原图不变"""
    from PIL import ImageOps

    im = Image.new("RGB", (20, 10))

    def mock_exif_transpose(_im, **kwargs):
        raise OSError(-2, "corrupted EXIF data")

    monkeypatch.setattr(ImageOps, "exif_transpose", mock_exif_transpose)
    out = parser_base.transpose_im(im)
    assert out.size == (20, 10)
    assert out.getexif().get(0x0112) is None


def test_validate_args_choiceenum_instance_branch(monkeypatch) -> None:
    """覆盖 validate_args 中 ChoiceEnum 分支"""

    class TestParser(parser_base.BaseParser):
        KEY = "test"
        ARGS = {
            "m": {"type": enums.ArgType.STRING.value, "choices": enums.ResizeMode},
        }

    # 在测试里将 ChoiceEnum 调整为 type，模拟 choices 为枚举类时走 values 分支
    monkeypatch.setattr(parser_base, "ChoiceEnum", type)
    assert TestParser.validate_args(m="lfit") == {"m": "lfit"}


@pytest.mark.usefixtures("clean_dir")
def test_has_transparency_and_animation_frame_copy() -> None:
    assert parser_base.has_transparency(Image.new("RGBA", (2, 2))) is True

    frame1 = Image.new("RGB", (8, 8), color=(255, 0, 0))
    frame2 = Image.new("RGB", (8, 8), color=(0, 0, 255))
    gif_path = "rgb-animation.gif"
    frame1.save(gif_path, save_all=True, append_images=[frame2], loop=0, duration=[80, 120], format="GIF")

    with Image.open(gif_path) as im:
        kwargs = parser_base.ImgSaveParser(animation=1).compute(im, im)
        assert kwargs["save_all"] is True
        assert len(kwargs["append_images"]) == im.n_frames - 1
        assert len(kwargs["duration"]) == im.n_frames
        assert all(isinstance(d, int) for d in kwargs["duration"])


def test_process_params() -> None:
    p = ProcessParams.parse_str("interlace,1/format,png")
    im = Image.new("RGBA", (200, 200))
    save_params = p.save_parser.compute(im, im)
    assert save_params == {"interlace": 1, "format": "png", "progressive": True}


@pytest.mark.usefixtures("mock_settings")
def test_validate_uri(monkeypatch, link_uri) -> None:
    monkeypatch.setattr(settings, "PROCESSOR_WORKSPACES", ("/tmp",))
    with pytest.raises(ParamValidateException, match="系统文件不存在"):
        parser_base.BaseParser._validate_uri("a/test.jpg")
    with pytest.raises(ParamValidateException, match="文件必须在 PROCESSOR_WORKSPACES"):
        parser_base.BaseParser._validate_uri("tests/imgs/lenna-400x225.jpg")

    monkeypatch.setattr(settings, "PROCESSOR_ALLOW_DOMAINS", (".githubusercontent.com",))
    # 无异常
    parser_base.BaseParser._validate_uri(link_uri)
    with pytest.raises(ParamValidateException, match="链接未解析出域名"):
        parser_base.BaseParser._validate_uri("http://")
    with pytest.raises(ParamValidateException, match="域名不合法"):
        parser_base.BaseParser._validate_uri("http://test.com/test.jpg")


def test_save_parser_keys_not_in_opaction() -> None:
    for k in parser_base.ImgSaveParser.ARGS.keys():
        assert k not in enums.OpAction
