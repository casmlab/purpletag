#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

#    include_package_data=True,

setup(
    name='purpletag',
    version='0.1.3',
    description='A tool to track hashtags used by members of the U.S. congress.',
    long_description=readme + '\n\n' + history,
    author='Aron Culotta',
    author_email='aronwc@gmail.com',
    url='https://github.com/casmlab'
        '/purpletag',
    packages=[
        'purpletag',
    ],
    package_dir={'purpletag':
                 'purpletag'},
    package_data={'purpletag': ['web/plot.html']},
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='purpletag',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        'console_scripts': [
            'purpletag = purpletag.purpletag:main',
            'purpletag-collect = purpletag.purpletag_collect:main',
            'purpletag-parse = purpletag.purpletag_parse:main',
            'purpletag-score = purpletag.purpletag_score:main',
            'purpletag-serve = purpletag.purpletag_serve:main',
        ],
    },
    test_suite='tests',
)
