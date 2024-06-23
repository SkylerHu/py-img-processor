#!/usr/bin/env python
# coding=utf-8
import typing
import pytest

from imgprocessor import settings, parsers
from imgprocessor.utils import base64url_encode
from imgprocessor.parsers import ProcessParams, _ACTION_PARASER_MAP
from imgprocessor.exceptions import ParamValidateException, ProcessLimitException, ParamParseException


def test_parse_define() -> None:
    """测试参数解析类的定义：类KEY和其属性的默认值是否一致"""
    for cls in _ACTION_PARASER_MAP.values():
        ins = cls()
        for key, config in cls.ARGS.items():
            _type = config["type"]
            if not config.get("required"):
                _default = config.get("default")
                msg = f"校验{cls.__name__}的属性{key}，类型{_type}，默认值{_default}"
                assert hasattr(ins, key), msg
                value = getattr(ins, key)
                assert value == _default, msg


@pytest.mark.parametrize(
    "param_str,action_num",
    [
        ("resize,s_200//xxx/format,jpeg/quality,75", 1),
        ("resize,s_200/xxx,s_1/crop,w_10", 2),
        ("resize,s_200,color_FFFFFF/crop,w_10", 2),
        ({"actions": [{"key": "xxx"}]}, 0),
        ({"actions": [{"key": "resize", "w": 100}]}, 1),
    ],
)
def test_parse_params(param_str: typing.Union[dict, str], action_num: int) -> None:
    if isinstance(param_str, dict):
        p = ProcessParams(**param_str)
    else:
        p = ProcessParams.parse_str(param_str)
    assert len(p.actions) == action_num


@pytest.mark.parametrize(
    "param_str,exception,error",
    [
        ("format,jpg", ParamValidateException, "参数 format 只能是其中之一"),
        ("quality,a", ParamValidateException, "参数类型不符合要求"),
        ("quality,0", ParamValidateException, "参数不在取值范围内"),
        ("quality,101", ParamValidateException, "参数不在取值范围内"),
        ("resize,m_xxx", ParamValidateException, "枚举值只能是其中之一"),
        ("resize,m_xxx/,", ParamParseException, "参数必须指定操作类型"),
        ("resize,s_100,color_xxx", ParamValidateException, "不符合格式要求"),
    ],
)
def test_parse_exception(param_str: typing.Union[dict, str], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(param_str, dict):
            ProcessParams(**param_str)
        else:
            ProcessParams.parse_str(param_str)


@pytest.mark.parametrize(
    "src_size,param_str,expected",
    [
        ((1920, 1080), "resize,w_1280", (1280, 720)),
        ((1920, 1080), "resize,h_720", (1280, 720)),
        # 范围内最大
        ((1920, 1080), "resize,m_lfit,w_1280,h_540", (960, 540)),
        ((1920, 1080), "resize,m_lfit,w_960,h_720", (960, 540)),
        # 范围外最小
        ((1920, 1080), "resize,m_mfit,w_1280", (1280, 720)),
        ((1920, 1080), "resize,m_mfit,h_720", (1280, 720)),
        ((1920, 1080), "resize,m_mfit,w_1280,h_540", (1280, 720)),
        ((1920, 1080), "resize,m_mfit,w_960,h_720", (1280, 720)),
        # 固定宽高，强制缩放
        ((1920, 1080), "resize,m_fixed,w_1280,h_540", (1280, 540)),
        # s/l参数
        ((1920, 1080), "resize,s_720", (1280, 720)),
        ((1080, 1920), "resize,s_720", (720, 1280)),
        ((1920, 1080), "resize,l_1280", (1280, 720)),
        ((1080, 1920), "resize,l_1280", (720, 1280)),
        # p
        ((1920, 1080), "resize,p_50", (960, 540)),
        ((1920, 1080), "resize,p_150", (1920, 1080)),
        ((1920, 1080), "resize,p_150,limit_0", (2880, 1620)),
    ],
)
def test_resize_compute(src_size: tuple, param_str: str, expected: tuple) -> None:
    """测试resize操作的参数处理

    Args:
        src_size: 输入图像的宽高(src_w, src_h)
        param_str: 处理参数
        expected: 期望输出的宽高(w, h)
    """
    action = parsers.ResizeParser.init_by_str(param_str)
    w, h = action.compute(*src_size)
    assert (w, h) == expected


@pytest.mark.parametrize(
    "src_size,params,exception,error",
    [
        # resize
        ((1920, 1080), "resize,m_lfit", ParamValidateException, "缺少合法参数"),
        ((1920, 1080), "resize,m_fixed,w_100", ParamValidateException, "参数w和h都必不可少"),
        ((1920, 1080), "resize,m_pad2", ParamValidateException, "枚举值只能是其中之一"),
        ((1920, 1080), "resize,w_a", ParamValidateException, "参数类型不符合要求"),
        ((1920, 1080), "resize,w_1.1", ParamValidateException, "必须是整数"),
        ((1920, 1080), "resize,w_0", ParamValidateException, "参数不在取值范围内"),
        ((1920, 1080), f"resize,w_{settings.PROCESSOR_MAX_W_H + 1}", ParamValidateException, "参数不在取值范围内"),
        ((1920, 1080), {"key": "resize", "w": 1.1}, ParamValidateException, "必须是整数"),
        ((1920, 1080), {"key": "resize", "color": 1}, ParamValidateException, "参数类型不符合要求"),
        ((1920, 1080), "resize,w_200000", ParamValidateException, "参数不在取值范围内"),
        ((1920, 1080), "resize,s_100,color_GGG", ParamValidateException, "不符合格式要求"),
        ((1920, 1080), "resize,w_25000,h_25000,limit_0", ProcessLimitException, "缩放的目标图像总像素不可超过"),
    ],
)
def test_resize_exception(src_size: tuple, params: typing.Union[str, dict], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(params, str):
            action = parsers.ResizeParser.init_by_str(params)
        else:
            action = parsers.ResizeParser.init(params)
        action.compute(*src_size)


@pytest.mark.parametrize(
    "src_size,param_str,expected",
    [
        ((1920, 1080), "crop,w_1280", (0, 0, 1280, 1080)),
        ((1920, 1080), "crop,h_720", (0, 0, 1920, 720)),
        ((1920, 1080), "crop,g_nw,w_960,h_540", (0, 0, 960, 540)),
        ((1920, 1080), "crop,g_north,w_960,h_540", (480, 0, 960, 540)),
        ((1920, 1080), "crop,g_ne,w_960,h_540", (960, 0, 960, 540)),
        ((1920, 1080), "crop,g_west,w_960,h_540", (0, 270, 960, 540)),
        ((1920, 1080), "crop,g_center,w_960,h_540", (480, 270, 960, 540)),
        ((1920, 1080), "crop,g_east,w_960,h_540", (960, 270, 960, 540)),
        ((1920, 1080), "crop,g_sw,w_960,h_540", (0, 540, 960, 540)),
        ((1920, 1080), "crop,g_south,w_960,h_540", (480, 540, 960, 540)),
        ((1920, 1080), "crop,g_se,w_960,h_540,pf_xywh", (960, 540, 960, 540)),
        ((1920, 1080), "crop,pf_xywh,x_25,y_25,w_50,h_50", (480, 270, 960, 540)),
        ((1920, 1080), "crop,padr_10,padb_10", (0, 0, 1910, 1070)),
        ((1920, 1080), "crop,w_1920,h_1080", (0, 0, 1920, 1080)),
        ((1920, 1080), "crop,pf_x", (0, 0, 1920, 1080)),
        ((1920, 1080), "crop,pf_y", (0, 0, 1920, 1080)),
        ((1920, 1080), "crop,ratio_1:1", (0, 0, 1080, 1080)),
        ((1920, 1080), "crop,ratio_16:9", (0, 0, 1920, 1080)),
        ((1080, 1920), "crop,ratio_16:9", (0, 0, 1080, 607)),
    ],
)
def test_crop_compute(src_size: tuple, param_str: str, expected: tuple) -> None:
    action = parsers.CropParser.init_by_str(param_str)
    out = action.compute(*src_size)
    assert out == expected


@pytest.mark.parametrize(
    "src_size,params,exception,error",
    [
        # resize
        ((1920, 1080), "crop,pf_xywh,w_101", ParamValidateException, "所以w作为百分比取值范围为"),
        ((1920, 1080), "crop,pf_xywh,h_101", ParamValidateException, "所以h作为百分比取值范围为"),
        ((1920, 1080), "crop,pf_xywh,x_101", ParamValidateException, "所以x作为百分比取值范围为"),
        ((1920, 1080), "crop,pf_xywh,y_101", ParamValidateException, "所以y作为百分比取值范围为"),
        ((1920, 1080), "crop,w_1921", ParamValidateException, "区域超过了原始图片"),
    ],
)
def test_crop_exception(src_size: tuple, params: typing.Union[str, dict], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(params, str):
            action = parsers.CropParser.init_by_str(params)
        else:
            action = parsers.CropParser.init(params)
        action.compute(*src_size)


@pytest.mark.parametrize(
    "src_size,param_str,expected",
    [
        ((1920, 1080), "circle,r_60", 60),
        ((1920, 1080), "circle", 540),
        ((1080, 1920), "circle", 540),
    ],
)
def test_circle_compute(src_size: tuple, param_str: str, expected: tuple) -> None:
    action = parsers.CircleParser.init_by_str(param_str)
    out = action.compute(*src_size)
    assert out == expected


@pytest.mark.parametrize(
    "src_size,params,exception,error",
    [
        ((1920, 1080), "circle,r_a", ParamValidateException, "参数类型不符合要求"),
    ],
)
def test_circle_exception(src_size: tuple, params: typing.Union[str, dict], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(params, str):
            action = parsers.CircleParser.init_by_str(params)
        else:
            action = parsers.CircleParser.init(params)
        action.compute(*src_size)


@pytest.mark.parametrize(
    "src_size,params,exception,error",
    [
        ((1920, 1080), "blur", ParamValidateException, "缺少必要参数"),
    ],
)
def test_blur_exception(src_size: tuple, params: typing.Union[str, dict], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(params, str):
            parsers.BlurParser.init_by_str(params)
        else:
            parsers.BlurParser.init(params)


@pytest.mark.usefixtures("clean_dir")
@pytest.mark.parametrize(
    "param_str,expected",
    [
        (f"watermark,image_{base64url_encode('wolf-50.png')}", (50, 50)),
        # 在8.0.0版本处理结果会是(189,48)，后后面小版本修复了
        (f"watermark,text_{base64url_encode('Hello 世界')},font_{base64url_encode('PingFang-Heavy.ttf')}", (190, 48)),
    ],
)
def test_wm_gen_im(param_str: str, expected: tuple) -> None:
    action = parsers.WatermarkParser.init_by_str(param_str)
    out = action.get_watermark_im()
    assert out.size == expected


@pytest.mark.usefixtures("clean_dir")
@pytest.mark.parametrize(
    "params,exception,error",
    [
        ("watermark,size_14", ParamValidateException, "image或者text参数必须传递一个"),
        (
            f"watermark,text_{base64url_encode('Hello 世界')},font_{base64url_encode('bk-PingFang-Heavy.ttf')}",
            ParamValidateException,
            "未找到字体",
        ),
    ],
)
def test_wm_exception(params: typing.Union[str, dict], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(params, str):
            action = parsers.WatermarkParser.init_by_str(params)
        else:
            action = parsers.WatermarkParser.init(params)
        action.get_watermark_im()


@pytest.mark.parametrize(
    "input_params,param_str,expected",
    [
        # 仅测试compute，参数image图像不存在
        ((1920, 1080, 1024, 768), "merge,image_aW1hZ2U,g_center", (1920, 1080, 0, 0, 448, 156)),
        ((1920, 1080, 1024, 768), "merge,image_aW1hZ2U,x_800,y_800", (1920, 1568, 0, 0, 800, 800)),
        ((768, 1024, 1920, 1080), "merge,image_aW1hZ2U,g_se", (1920, 1080, 1152, 56, 0, 0)),
        ((768, 1080, 1920, 1024), "merge,image_aW1hZ2U,g_se", (1920, 1080, 1152, 0, 0, 56)),
        ((768, 1024, 1920, 1080), "merge,image_aW1hZ2U,order_0", (2688, 1080, 0, 56, 768, 0)),
    ],
)
def test_merge_compute(input_params: tuple, param_str: str, expected: tuple) -> None:
    action = parsers.MergeParser.init_by_str(param_str)
    out = action.compute(*input_params)
    assert out == expected
