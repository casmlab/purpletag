#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
from os.path import basename
import yaml

from . import config


def get_basenames(files):
    """ Return basename of each file. E.g.:
    >>> get_basenames(['/foo/bar.1.2'])
    ['bar.1']
    """
    return [basename(f)[:basename(f).rfind('.')] for f in files]


def get_files(subdir, extension):
    """ Return all files in a subdirectory matching this extension. """
    return glob.glob(config.get('data', 'path') + '/' +
                     config.get('data', subdir) + '/*.' + extension)


def parse_twitter_handles():
    yaml_doc = yaml.load(open(config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml'), 'r'))
    return [d for d in yaml_doc if 'twitter' in d['social']]


def parse_legislators():
    yaml_doc = yaml.load(open(config.get('data', 'path') + '/' + config.get('data', 'leg_yaml'), 'r'))
    return [d for d in yaml_doc]
