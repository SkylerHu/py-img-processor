#!/usr/bin/env python
# coding=utf-8
import os
import pytest
import tempfile


@pytest.fixture
def clean_dir():
    with tempfile.TemporaryDirectory() as new_path:
        old_cwd = os.getcwd()
        os.chdir(new_path)
        yield
        os.chdir(old_cwd)
