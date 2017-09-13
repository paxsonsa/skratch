# -*- coding: utf-8 -*-
""" Test Skratchlib

Author: Andrew Paxson
Created: 2017-09-12
"""
import pytest

import skratchlib


@pytest.mark.parametrize("files, expected", (
    (["scratch1"], "2"),
    (["scratch243", "scratch43"], "244"),
    (["scratch"],"1"),))
def test_next_file_number(files, expected):
    num = skratchlib._next_file_number(files, "scratch(\d+)")
    assert num == expected


def test_create_new_scratch_file():
    import os
    # Settings
    settings = skratchlib.SettingData()
    settings.location = os.getcwd()
    settings.editor = "echo"

    # Test Empty new file
    path = skratchlib.create_new_scratch_file("", settings)
    assert os.path.basename(path) == "scratch"
    assert os.path.exists(path)
    os.remove(path)

    # Test Named File
    path = skratchlib.create_new_scratch_file("testfile", settings)
    assert os.path.basename(path) == "testfile"
    assert os.path.exists(path)
    os.remove(path)


def test_cli_parser():
    settings = skratchlib.SettingData()
    skratchlib.cli_parser(settings)