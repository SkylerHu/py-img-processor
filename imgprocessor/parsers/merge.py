#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image

from imgprocessor import enums, settings
from .base import BaseParser, pre_processing, compute_by_geography, compute_splice_two_im


class MergeParser(BaseParser):

    KEY = enums.OpAction.MERGE
    ARGS = {
        # 要处理的图片
        "image": {"type": enums.ArgType.STRING, "required": True, "base64_encode": True},
        # 对image的处理参数
        "action": {"type": enums.ArgType.STRING, "base64_encode": True},
        # 使用输入图像的大小作为参照进行缩放
        "p": {"type": enums.ArgType.INTEGER, "default": 0, "min": 1, "max": 1000},
        # 对齐方式
        "order": {"type": enums.ArgType.INTEGER, "choices": enums.PositionOrder},
        "align": {"type": enums.ArgType.INTEGER, "default": enums.PositionAlign.BOTTOM, "choices": enums.PositionAlign},
        "interval": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 1000},
        # 粘贴的位置
        "g": {"type": enums.ArgType.STRING, "choices": enums.Geography},
        "x": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "y": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "pf": {"type": enums.ArgType.STRING, "default": ""},
        # 拼接后大小包含2个图像，空白区域使用color颜色填充
        "color": {
            "type": enums.ArgType.STRING,
            "default": "FFFFFF",
            "regex": r"^([0-9a-fA-F]{6}|[0-9a-fA-F]{8}|[0-9a-fA-F]{3,4})$",
        },
    }

    def __init__(
        self,
        image: typing.Optional[str] = None,
        action: typing.Optional[str] = None,
        p: int = 0,
        order: typing.Optional[int] = None,
        align: int = 2,
        interval: int = 0,
        g: typing.Optional[str] = None,
        x: int = 0,
        y: int = 0,
        pf: str = "",
        color: str = "FFFFFF",
        **kwargs: typing.Any,
    ) -> None:
        self.image = image
        self.action = action
        self.p = p
        self.order = order
        self.align = align
        self.interval = interval
        self.g = g
        self.x = x
        self.y = y
        self.pf = pf
        self.color = color

    def compute(self, src_w: int, src_h: int, w2: int, h2: int) -> tuple:
        if self.order in enums.PositionOrder:  # type: ignore
            order = typing.cast(int, self.order)
            w, h, x1, y1, x2, y2 = compute_splice_two_im(
                src_w,
                src_h,
                w2,
                h2,
                align=self.align,
                order=order,
                interval=self.interval,
            )
        else:
            x, y = compute_by_geography(src_w, src_h, self.x, self.y, w2, h2, self.g, self.pf)
            x1, y1, x2, y2 = 0, 0, x, y
            if x < 0:
                # 一般是因为第2张图像大小大于第1张
                x1, x2 = -x, 0
            if y < 0:
                y1, y2 = -y, 0

            # 计算新建画布的大小
            w, h = max(x + w2, src_w, w2), max(y + h2, src_h, h2)

        return w, h, x1, y1, x2, y2

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im, use_alpha=True)
        src_w, src_h = im.size

        im2 = Image.open(self.image)
        im2 = pre_processing(im2, use_alpha=True)
        if self.action:
            from imgprocessor.processor import ProcessParams, handle_img_actions

            params = ProcessParams.parse_str(self.action)
            im2 = handle_img_actions(im2, params.actions)
        if self.p:
            w2, h2 = round(src_w * self.p / 100), round(src_h * self.p / 100)
            im2 = im2.resize((w2, h2), resample=Image.LANCZOS)
        w2, h2 = im2.size

        w, h, x1, y1, x2, y2 = self.compute(src_w, src_h, w2, h2)
        out = Image.new("RGBA", (w, h), color=f"#{self.color}")
        out.paste(im, (x1, y1), im)
        out.paste(im2, (x2, y2), im2)
        return out
