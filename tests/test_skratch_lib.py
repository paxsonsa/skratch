# -*- coding: utf-8 -*-
""" Test Skratchlib

Author: Andrew Paxson
Created: 2017-09-12
"""
import os
import pytest

import skratchlib

TEST_LOCATION = os.path.join(os.getcwd(), "testdir")


@pytest.fixture()
def test_files():

    os.mkdir(TEST_LOCATION)

    scratch_files = [
        "scratch1", "flirt", "THISONE"
    ]
    for f in scratch_files:
        with open(os.path.join(TEST_LOCATION, f), 'w') as fh:
            fh.write("Hello, {0}".format(f))

    yield TEST_LOCATION, scratch_files

    print("Cleaning Up...")
    for f in scratch_files:
        os.remove(os.path.join(TEST_LOCATION, f))
    os.removedirs(TEST_LOCATION)


@pytest.fixture()
def location():
    os.mkdir(TEST_LOCATION)
    yield TEST_LOCATION
    os.removedirs(TEST_LOCATION)


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
    os.remove(path)     # Clean Up


def test_get_most_recently_modified_scratch_empty(location):
    settings = skratchlib.SettingData()
    settings.location = location
    settings.editor = "echo"

    # Test Return "" when no files exist
    fp = skratchlib.get_recently_modified_scratch_file(settings)
    assert fp == ""


def test_get_most_recently_modified_scratch(test_files):
    # Settings
    settings = skratchlib.SettingData()
    settings.location = test_files[0]

    latest = os.path.join(settings.location, test_files[1][-1])

    fp = skratchlib.get_recently_modified_scratch_file(settings)
    assert fp == latest

# TODO Create Actions Tests for CLI Component

def test_cli_parser():
    settings = skratchlib.SettingData()
    skratchlib.cli_parser(settings)
