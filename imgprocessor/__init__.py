import typing
import os
import traceback
import importlib


__all__ = ["settings", "VERSION"]
__version__ = "1.2.0"


VERSION = __version__

_BLACK_ATTRS = ["_settings", "__dict__"]


class SettingsProxy(object):

    def __init__(self) -> None:
        _settings = None
        # 兼容在Django项目中的使用
        _settings_module = os.environ.get("PY_SETTINGS_MODULE") or os.environ.get("DJANGO_SETTINGS_MODULE")
        try:
            if _settings_module:
                _settings = importlib.import_module(_settings_module)
        except Exception:
            traceback.print_exc()
            print('Please set the correct "PY_SETTINGS_MODULE".')

        self._settings = _settings

    # 是否调试模式
    DEBUG = False

    # 处理原图的大小限制， 单位 MB
    PROCESSOR_MAX_FILE_SIZE = 20
    # 处理图像，原图宽高像素限制
    PROCESSOR_MAX_W_H = 30000
    # width x height总像素3亿，处理前后的值都被此配置限制
    PROCESSOR_MAX_PIXEL = 300000000
    # 图像处理后的默认质量
    PROCESSOR_DEFAULT_QUALITY = 75
    # 默认字体文件; 默认配置了MacOS系统中的字体
    PROCESSOR_TEXT_FONT = "Arial Unicode.ttf"
    # 工作目录列表：例如水印文件必须限制在设定的目录下，避免恶意访问文件
    PROCESSOR_WORKSPACES = ()
    # 当资源文件uri使用链接地址时，限制地址域名来源
    PROCESSOR_ALLOW_DOMAINS = ()

    def __getattribute__(self, attr: str) -> typing.Any:
        try:
            if attr in _BLACK_ATTRS:
                # 白名单，内置属性直接返回
                return super(SettingsProxy, self).__getattribute__(attr)

            if self._settings is not None and hasattr(self._settings, attr):
                value = getattr(self._settings, attr)
            else:
                value = super(SettingsProxy, self).__getattribute__(attr)
        except AttributeError:
            raise AttributeError('settings has no attribute "{}"'.format(attr))
        return value

    def __setattr__(self, name: str, value: typing.Any) -> None:
        if name in _BLACK_ATTRS and not hasattr(self, name):
            return super(SettingsProxy, self).__setattr__(name, value)
        raise AttributeError("All properties of settings are not allowed to be changed.")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("All properties of settings are not allowed to be changed.")


settings = SettingsProxy()
