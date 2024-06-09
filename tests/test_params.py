#!/usr/bin/env python
# coding=utf-8
import typing
import pytest

from imgprocessor import enums, settings
from imgprocessor.params import ResizeAction
from imgprocessor.exceptions import ParamParseException, ParamValidateException


@pytest.mark.parametrize(
    "src_size,param_str,expected",
    [
        ((1920, 1080), "w_1280", (1280, 720)),
        ((1920, 1080), "h_720", (1280, 720)),
        # 范围内最大
        ((1920, 1080), "m_lfit,w_1280,h_540", (960, 540)),
        ((1920, 1080), "m_lfit,w_960,h_720", (960, 540)),
        # 范围外最小
        ((1920, 1080), "m_mfit,w_1280", (1280, 720)),
        ((1920, 1080), "m_mfit,h_720", (1280, 720)),
        ((1920, 1080), "m_mfit,w_1280,h_540", (1280, 720)),
        ((1920, 1080), "m_mfit,w_960,h_720", (1280, 720)),
        # 固定宽高，强制缩放
        ((1920, 1080), "m_fixed,w_1280,h_540", (1280, 540)),
        # s/l参数
        ((1920, 1080), "s_720", (1280, 720)),
        ((1080, 1920), "s_720", (720, 1280)),
        ((1920, 1080), "l_1280", (1280, 720)),
        ((1080, 1920), "l_1280", (720, 1280)),
        # p
        ((1920, 1080), "p_50", (960, 540)),
        ((1920, 1080), "p_150", (2880, 1620)),
    ],
)
def test_resize_compute(src_size: tuple, param_str: str, expected: tuple) -> None:
    """测试resize操作的参数处理

    Args:
        src_size: 输入图片的宽高(src_w, src_h)
        param_str: 处理参数
        expected: 期望输出的宽高(w, h)
    """
    action = ResizeAction.init_by_str(f"{enums.OpAction.RESIZE},{param_str}")
    w, h = action.compute(*src_size)
    assert (w, h) == expected


@pytest.mark.parametrize(
    "src_size,params,exception,error",
    [
        # resize
        ((1920, 1080), "resize,m", ParamParseException, "下划线隔开的格式"),
        ((1920, 1080), "resize,m_lfit", ParamValidateException, "缺少合法参数"),
        ((1920, 1080), "resize,m_fixed,w_100", ParamValidateException, "参数w和h都必不可少"),
        ((1920, 1080), "resize,m_pad", ParamValidateException, "枚举值只能是其中之一"),
        ((1920, 1080), "resize,w_a", ParamValidateException, "参数类型不符合要求"),
        ((1920, 1080), "resize,w_1.1", ParamValidateException, "必须是整数"),
        ((1920, 1080), "resize,w_0", ParamValidateException, "参数不在取值范围内"),
        ((1920, 1080), f"resize,w_{settings.PROCESSOR_MAX_W_H + 1}", ParamValidateException, "参数不在取值范围内"),
        ((1920, 1080), {"key": "resize", "w": 1.1}, ParamValidateException, "必须是整数"),
        ((1920, 1080), {"key": "resize", "color": 1}, ParamValidateException, "参数类型不符合要求"),
        ((1920, 1080), "resize,w_200000", ParamValidateException, "参数不在取值范围内"),
        ((1920, 1080), "resize,color_fff", ParamValidateException, "不符合格式要求"),
    ],
)
def test_action_exception(src_size: tuple, params: typing.Union[str, dict], exception: Exception, error: str) -> None:
    with pytest.raises(exception, match=error):
        if isinstance(params, str):
            action = ResizeAction.init_by_str(params)
        else:
            action = ResizeAction.init(params)
        action.compute(*src_size)
