"""
修复 README 中的相对路径，使其在 mkdocs 中正常工作。

README.md 位于项目根目录，使用 ``./docs/imgs/...`` 等路径引用资源。
当通过软链接 ``docs/README.md → ../README.md`` 在 ``docs_dir: docs/`` 下构建时，
``./docs/`` 前缀会导致路径解析到不存在的 ``docs/docs/`` 目录，需要去除该前缀。

同时将中英文切换链接（README.zh.md / README.md）重写为 mkdocs-static-i18n
插件生成的语言 URL，确保链接在构建后的站点中正常跳转。
"""

from __future__ import annotations

import re
from typing import Any


def on_page_markdown(markdown: str, page: Any, config: Any, files: Any) -> str:
    # 仅对根目录的 README / index 页面生效
    if page.file.name not in ("README", "index"):
        return markdown

    # 去除多余的 "./docs/" 前缀
    # 示例: "](./docs/imgs/foo.png)" → "](imgs/foo.png)"
    markdown = re.sub(r"\]\(\./docs/", "](", markdown)

    # 将语言切换链接重写为相对路径（兼容 Read the Docs 多版本 URL）
    # 中文页 (/zh/): [English](README.md) → [English](../)   从 /zh/ 向上回到根
    # 英文页 (/):    [中文文档](README.zh.md) → [中文文档](zh/) 从根进入 /zh/
    locale = getattr(page.file, "locale", None)
    if locale == "zh":
        markdown = re.sub(r"\]\(README\.md\)", "](../)", markdown)
    else:
        markdown = re.sub(r"\]\(README\.zh\.md\)", "](zh/)", markdown)

    return markdown
