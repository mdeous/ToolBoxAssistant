# -*- coding: utf-8 -*-
import os
import tempfile


class chdir(object):
    """
    Context-manager that changes current directory on enter, and
    go back to previous directory on exit.
    """
    def __init__(self, dirname):
        self.orig_dir = os.getcwd()
        self.dest_dir = os.path.realpath(dirname)

    def __enter__(self):
        os.chdir(self.dest_dir)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.orig_dir)


def unnest_dir(dirname):
    """
    Move inner directory to outer's directory location.
    Useful when archive data is in a subfolder and outer folder
    contains nothing else.
    """
    outer_content = os.listdir(dirname)
    if (len(outer_content) != 1) or not os.path.isdir(os.path.join(dirname, outer_content[0])):
        return
    inner_dir = os.path.join(dirname, outer_content[0])
    temp_dir = os.path.join(tempfile.gettempdir(), outer_content[0])
    os.renames(inner_dir, temp_dir)
    os.renames(temp_dir, dirname)
