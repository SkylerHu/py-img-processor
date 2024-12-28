#!/usr/bin/env python
# coding=utf-8
import typing

from PIL import Image, ImageFont, ImageDraw

from imgprocessor import enums, settings, utils
from imgprocessor.exceptions import ParamValidateException
from .base import BaseParser, pre_processing, compute_splice_two_im, compute_by_geography, trans_uri_to_im


class WatermarkParser(BaseParser):

    KEY = enums.OpAction.WATERMARK
    ARGS = {
        # 水印本身的不透明度，100表示完全不透明
        "t": {"type": enums.ArgType.INTEGER, "default": 100, "min": 0, "max": 100},
        "g": {"type": enums.ArgType.STRING, "choices": enums.Geography},
        "x": {"type": enums.ArgType.INTEGER, "default": 10, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        "y": {"type": enums.ArgType.INTEGER, "default": 10, "min": 0, "max": settings.PROCESSOR_MAX_W_H},
        # percent field, eg: xy
        "pf": {"type": enums.ArgType.STRING, "default": ""},
        # 是否将图片水印或文字水印铺满原图; 值为1开启
        "fill": {"type": enums.ArgType.INTEGER, "default": 0, "choices": [0, 1]},
        "padx": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 4096},
        "pady": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 4096},
        # 图片水印路径
        "image": {"type": enums.ArgType.URI, "base64_encode": True},
        # 水印的原始设计参照尺寸，会根据原图大小缩放水印
        "design": {"type": enums.ArgType.INTEGER, "min": 1, "max": settings.PROCESSOR_MAX_W_H},
        # 文字
        "text": {"type": enums.ArgType.STRING, "base64_encode": True, "max_length": 64},
        "font": {"type": enums.ArgType.STRING, "base64_encode": True},
        # 文字默认黑色
        "color": {"type": enums.ArgType.STRING, "default": "000000", "regex": "^([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$"},
        "size": {"type": enums.ArgType.INTEGER, "default": 40, "min": 1, "max": 1000},
        # 文字水印的阴影透明度, 0表示没有阴影
        "shadow": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 100},
        # 顺时针旋转角度
        "rotate": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 360},
        # 图文混合水印参数
        # 文字和图片水印的前后顺序; 0表示图片水印在前；1表示文字水印在前
        "order": {"type": enums.ArgType.INTEGER, "default": enums.PositionOrder.BEFORE, "choices": enums.PositionOrder},
        # 文字水印和图片水印的对齐方式; 0表示文字水印和图片水印上对齐; 1表示文字水印和图片水印中对齐; 2: 表示文字水印和图片水印下对齐
        "align": {"type": enums.ArgType.INTEGER, "default": enums.PositionAlign.BOTTOM, "choices": enums.PositionAlign},
        # 文字水印和图片水印间的间距
        "interval": {"type": enums.ArgType.INTEGER, "default": 0, "min": 0, "max": 1000},
    }

    def __init__(
        self,
        t: int = 100,
        g: typing.Optional[str] = None,
        x: int = 10,
        y: int = 10,
        pf: str = "",
        fill: int = 0,
        padx: int = 0,
        pady: int = 0,
        image: typing.Optional[str] = None,
        design: typing.Optional[int] = None,
        text: typing.Optional[str] = None,
        font: typing.Optional[str] = None,
        color: str = "000000",
        size: int = 40,
        shadow: int = 0,
        rotate: int = 0,
        order: int = 0,
        align: int = 2,
        interval: int = 0,
        **kwargs: typing.Any,
    ) -> None:
        self.t = t
        self.g = g
        self.x = x
        self.y = y
        self.pf = pf
        self.fill = fill
        self.padx = padx
        self.pady = pady
        self.image = image
        self.design = design
        self.text = text
        self.font = font
        self.color = color
        self.size = size
        self.shadow = shadow
        self.rotate = rotate
        self.order = order
        self.align = align
        self.interval = interval

    def validate(self) -> None:
        super().validate()
        if not self.image and not self.text:
            raise ParamValidateException("image或者text参数必须传递一个")

    def get_watermark_im(self) -> Image:
        """初始化水印对象"""
        w1, h1, w2, h2 = 0, 0, 0, 0
        icon = None
        if self.image:
            icon = trans_uri_to_im(self.image)
            icon = pre_processing(icon, use_alpha=True)
            if not self.text:
                # 没有文字，直接返回
                return icon
            w1, h1 = icon.size

        try:
            _font_path = self.font or settings.PROCESSOR_TEXT_FONT
            font = ImageFont.truetype(_font_path, self.size)
        except OSError:
            raise ParamValidateException(f"未找到字体 {_font_path}")

        if utils.get_pil_version() >= utils.Version("10.0.0"):
            _, _, w2, h2 = font.getbbox(self.text)
        else:
            w2, h2 = font.getsize(self.text)

        w, h, x1, y1, x2, y2 = compute_splice_two_im(
            w1,
            h1,
            w2,
            h2,
            align=self.align,
            order=self.order,
            interval=self.interval,
        )

        mark = Image.new("RGBA", (w, h))
        draw = ImageDraw.Draw(mark, mode="RGBA")

        # 阴影要单独处理透明度，放在文字之前处理
        if self.shadow:
            offset = max(round(self.size / 20), 2)
            shadow_color = "#000000"
            # 左上到右下的阴影，只保留这一个
            draw.text((x2 + offset, y2 + offset), self.text, font=font, fill=shadow_color)
            # draw.text((x2 - offset, y2 + offset), self.text, font=font, fill=shadow_color)
            # draw.text((x2 + offset, y2 - offset), self.text, font=font, fill=shadow_color)
            # draw.text((x2 - offset, y2 - offset), self.text, font=font, fill=shadow_color)
            _, _, _, alpha_channel = mark.split()
            alpha_channel = alpha_channel.point(lambda i: min(round(255 * self.shadow / 100), i))
            mark.putalpha(alpha_channel)

        # 处理文字
        draw.text((x2, y2), self.text, font=font, fill=f"#{self.color}")

        if icon:
            # icon放在文字之后粘贴，是因为文字要做一些其他处理
            mark.paste(icon, (x1, y1), icon)

        return mark

    def do_action(self, im: Image) -> Image:
        im = pre_processing(im, use_alpha=True)
        src_w, src_h = im.size

        pf = self.pf or ""
        if self.g:
            # g在的时候pf不生效
            pf = ""

        mark = self.get_watermark_im()
        w, h = mark.size

        if self.design:
            # 处理缩放
            rate = min(src_w, src_h) / self.design
            if rate != 1:
                w, h = round(w * rate), round(h * rate)
                mark = mark.resize((w, h), resample=Image.LANCZOS)

        if 0 < self.rotate < 360:
            # 处理旋转
            mark = mark.rotate(360 - self.rotate, expand=True)
            # 旋转会改变大小
            w, h = mark.size

        if w > src_w or h > src_h:
            # 水印大小超过原图了, 原图矩形内的最大图像
            if w / h > src_w / src_h:
                w, h = src_w, round(src_w * h / w)
                self.x = 0
            else:
                w, h = round(src_h * w / h), src_h
                self.y = 0
            mark = mark.resize((w, h), resample=Image.LANCZOS)

        if self.t < 100:
            # 处理透明度
            _, _, _, alpha_channel = mark.split()
            alpha_channel = alpha_channel.point(lambda i: min(round(255 * self.t / 100), i))
            mark.putalpha(alpha_channel)

        # 计算位置，粘贴水印
        x, y = compute_by_geography(src_w, src_h, self.x, self.y, w, h, self.g, pf)
        im.paste(mark, (x, y), mark)

        if self.fill:
            # 铺满整个图片
            # 寻找平铺最左上角的原点
            wx, wy = x, y
            while wx > 0:
                wx = wx - w - self.padx
            while wy > 0:
                wy = wy - h - self.pady
            # 往右下角方向平铺
            ux = wx
            while ux <= src_w:
                uy = wy
                while uy <= src_h:
                    if (ux, uy) != (x, y):
                        im.paste(mark, (ux, uy), mark)
                    uy = uy + h + self.pady
                ux = ux + w + self.padx

        return im
