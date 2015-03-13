# -*- coding: utf-8 -*-
import os
import tempfile
from subprocess import Popen, PIPE


class Color(object):
    BLUEBOLD = '\033[1;34m'
    GREENBOLD = '\033[1;32m'
    REDBOLD = '\033[1;31m'
    RED = '\033[0;31m'
    END = '\033[0m'


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


def find_versionned_folders(path):
    for root, subdirs, files in os.walk(path):
        for cvsdir in ('.git', '.svn', '.hg'):
            if cvsdir in subdirs:
                yield cvsdir.strip('.'), root
                break


def get_svn_url(regex, path):
    with chdir(path):
        p = Popen('LANG=en svn info', stdout=PIPE, stderr=PIPE, shell=True)
    svn_info, _ = p.communicate()
    url = regex.search(svn_info).group(1)
    return url


def readfile(path):
    with open(path) as ifile:
        content = ifile.read()
    return content


def yes_no(q):
    answer = None
    while answer is None:
        i = raw_input('%s [Y/n]' % q)
        if i in ('', 'y', 'Y', 'n', 'N'):
            answer = i
    return answer in ('', 'y', 'Y')
