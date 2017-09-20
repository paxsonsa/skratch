# -*- coding: utf-8 -*-
""" skratchlib

Library Package for Skratch Tool

Author: Andrew Paxson
Created: 2017-09-01
"""
#TODO Add List Scratch Files
import argparse
import os
import re
import subprocess

SCRATCH_FILENAME_CONSTANT = "scratch"
SCRATCH_LOCATION_CONSTANT = os.path.expanduser("~")
SCRATCH_RE_PATTERN_CONSTANT = r"{0}(\d+)"
SCRATCH_DEFAULT_EDITOR = "sublime"


class CLIComponent(object):
    def __init__(self, settings):
        self.settings = settings

    def action(self, args):
        raise NotImplementedError("action method needs to be implemented on {0}".format(self.__class__.__name__))


class NewScratchDelegate(CLIComponent):
    def action(self, args):
        """ Create New Scratch File """
        create_new_scratch_file(args.file, self.settings, py_template_func)

    def add_cli(self, subparser):
        """ Creates New Scratch CLI Interface on the given argparse.subparser

        Args:
            subparser (argparse._SubParsersAction): action to add arguments too

        Returns:
            argparse._SubParsersAction
        """
        new_parser = subparser.add_parser('create', help='create new scratch file')
        new_parser.add_argument('name', nargs='?', default=None, help="Optional Name to be given to the file, "
                                                                      "default name  is an increment of 'scratch##'")
        new_parser.set_defaults(func=self.action)
        return subparser


class RunScratchDelegate(CLIComponent):

    def action(self, args):
        file_ = args.file
        if not file_:
            file_ = get_recently_modified_scratch_file(self.settings)
        if not file_:
            raise RuntimeError("could not location files to run!")
        run_scratch_file(file_, self.settings)

    def add_cli(self, subparser):
        new_parser = subparser.add_parser('run', help='runscratch file')
        new_parser.add_argument('file', nargs='?', default="", help="Optional scratch filename to run, if not given "
                                                                    "it will run skratch with the latest mtime")
        new_parser.set_defaults(func=self.action)
        return subparser


class SettingData(object):
    def __init__(self):
        self.location = SCRATCH_LOCATION_CONSTANT
        self.editor = SCRATCH_DEFAULT_EDITOR
        self.base_filename = SCRATCH_FILENAME_CONSTANT
        self._re_pattern = SCRATCH_RE_PATTERN_CONSTANT.format(self.base_filename)

    @property
    def re_pattern(self):
        return self._re_pattern.format(self.base_filename)

    @re_pattern.setter
    def re_pattern(self, value):
        self._re_pattern = value


# ----------------------------------------------------------------------------
def _get_mtime(f):
    return os.stat(f).st_mtime


def _next_file_number(files, pattern):
    if not files:
        return ""
    numbers = []
    for f in files:
        num = re.findall(pattern, f)
        if num:
            numbers.append(int(num[0]))
    if numbers:
        return str(max(numbers) + 1)
    return "1"


def _open_with_editor(path, editor):
    return os.system("%s %s" % (path, editor))


def py_template_func(settings):
    return "#! /usr/bin/env python\n"


def create_new_scratch_file(file_name, settings, template_func=py_template_func):
    """ Creates New Scratch File

        Args:
            file_name (str)
            settings (SettingData)
            template_func (types.FunctionType)
    """
    if not file_name:
        re_pattern = settings.re_pattern

        def _filter_scratch_files(f):
            return re.match(re_pattern, f)

        files = os.listdir(settings.location)
        scratch_files = filter(_filter_scratch_files, files)
        num = _next_file_number(scratch_files, re_pattern)
        file_name = settings.base_filename + num

    path = os.path.join(SCRATCH_LOCATION_CONSTANT, file_name)
    with open(path, 'w') as fh:
        fh.write(template_func(settings))

    _open_with_editor(path, SCRATCH_DEFAULT_EDITOR)
    return path
    # paths = map(lambda x: os.path.join(settings.scratch_location, x), scratch_files)


def get_recently_modified_scratch_file(settings):
    """ Returns the most recently modified scratch in skratch dir

    Args:
        settings (SettingData): settings to use for getting scratch dir

    Returns:
        filepath (str) or empty string is nothing was found
    """
    dir_contents = os.listdir(settings.location)
    full_paths = map(lambda f: os.path.join(settings.location, f), dir_contents)
    files = filter(lambda  f: os.path.isfile(str(f)), full_paths)
    if not files:
        return ""
    files = sorted(files, key=_get_mtime)
    return files[-1]


def run_scratch_file(file_name, settings):
    """ Runs Given Scratch Filename with settings """
    return subprocess.call([file_name])


def cli_parser(settings):
    """ CLI Interface """
    parser = argparse.ArgumentParser("Scratch File Manager")
    subparser = parser.add_subparsers()

    cli_components = [
        NewScratchDelegate,
        RunScratchDelegate
    ]

    for component in cli_components:
        item = component(settings)
        item.add_cli(subparser)
    return parser