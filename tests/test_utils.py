#!/usr/bin/env python
# coding=utf-8
import pytest
import base64

from imgprocessor import utils


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello 世界", ""),
        ("Hello世界", "/"),
        ("Hello World", "="),
    ],
)
def test_bse64(text: str, expected: str) -> None:
    s = utils.base64url_encode(text)
    if expected:
        assert expected in base64.b64encode(text.encode()).decode()
    assert "+" not in s
    assert "/" not in s
    assert not s.endswith("=")
    assert utils.base64url_decode(s) == text
