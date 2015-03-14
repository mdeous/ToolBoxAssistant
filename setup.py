#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from setuptools import setup, find_packages

from ToolBoxAssistant import VERSION


setup(
    name='ToolBoxAssistant',
    version=VERSION,
    description='An utility to easily manage your toolbox applications',
    long_description=open(os.path.join(os.path.realpath(os.path.dirname(__file__)), 'README.md')).read(),
    author='Mathieu D. (MatToufoutu)',
    author_email='mattoufootu+code@gmail.com',
    url='https://github.com/mattoufoutu/ToolBoxAssistant',
    license='GPL',
    keywords='toolbox tools applications management utility',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    scripts=[os.path.join('.', 'ToolBoxAssistant', 'bin', 'tba')]
)
