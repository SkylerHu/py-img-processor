#!/usr/bin/env python
# coding=utf-8
import pytest
import os
import pathlib

import imgprocessor.processor
from imgprocessor.main import main


@pytest.mark.usefixtures("clean_dir")
@pytest.mark.parametrize(
    "argv,code",
    [
        ("-P expected/  -O tmp/test  --action resize,s_200/format,webp --overwrite", 0),
        ("-P dir1/  -O tmp/test  --action resize,s_200 --overwrite", 0),
        ("-P expected/  -O tmp/test2  --action resize,s_200 --overwrite", 1),
        ("-P lenna-400x225.jpg  -O expected/  --action resize,s_200 resize,l_200 --overwrite", 0),
        ("-P lenna-400x225.jpg  -O expected/lenna-edit.png  --action resize,s_200 --overwrite", 0),
        ("-P lenna-400x225.jpg  -O ./  --action resize,s_200", 1),
    ],
)
def test_run_main(argv: str, code: int, monkeypatch) -> None:
    USE_DIR = "tmp/test"
    if not os.path.exists(USE_DIR):
        os.makedirs(USE_DIR)
    # 新建个文件用于测试overwrite参数
    tmp_file = os.path.join(USE_DIR, "lenna-400x225.jpg")
    pathlib.Path(tmp_file).touch()
    assert os.path.isfile(tmp_file) is True

    monkeypatch.setattr(imgprocessor.processor, "process_image", lambda *args, **kwargs: True)
    assert main(argv=argv.split()) == code


@pytest.mark.usefixtures("clean_dir")
def test_img_use_main() -> None:
    img_path = "lenna.jpg"
    assert not os.path.isfile(img_path)

    argv = f"-P {img_path}  -O ./  --action resize,s_200"
    assert main(argv=argv.split()) == 1
