#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import io
import os
from os.path import basename
import requests
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


def fetch_twitter_handles():
    """ Fetch twitter handles from govtrack. """
    print 'fetching legislator Twitter handles from GovTrack...'
    text = requests.get(config.get('govtrack', 'handles')).text
    fp = open(config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml'), 'w')
    fp.write(text)
    fp.close()


def fetch_legislators():
    """ Download yaml of legislator info from GovTrack. """
    print 'fetching legislators from GovTrack...'
    text = requests.get(config.get('govtrack', 'legislators')).text
    fp = io.open(config.get('data', 'path') + '/' + config.get('data', 'leg_yaml'), mode='wt', encoding='utf8')
    fp.write(text)
    fp.close()


def parse_twitter_handles():
    yaml_doc_path = config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml')
    if not os.path.isfile(yaml_doc_path):
        fetch_twitter_handles()
    yaml_doc = yaml.load(open(yaml_doc_path, 'r'))
    return [d for d in yaml_doc if 'twitter' in d['social']]


def parse_legislators():
    yaml_doc_path = config.get('data', 'path') + '/' + config.get('data', 'leg_yaml')
    if not os.path.isfile(yaml_doc_path):
        fetch_legislators()
    yaml_doc = yaml.load(open(yaml_doc_path, 'r'))
    return [d for d in yaml_doc]


def twitter_handle_to_party():
    """ Read YAML files from GovTrack and map twitter handle to party. We
    restrict to Republican/Democrat.
    FIXME: This assumes bioguide ids always exist. We also assume that the party of your last term is your party.
    """
    twitter_handles = parse_twitter_handles()
    bioguide2handle = dict([(t['id']['bioguide'], t['social']['twitter'].lower()) for t in twitter_handles])
    legislators = parse_legislators()
    handle2party = dict()
    for leg in legislators:
        if leg['id']['bioguide'] in bioguide2handle:
            party = leg['terms'][0]['party']
            if party in ['Republican', 'Democrat']:
                handle2party[bioguide2handle[leg['id']['bioguide']]] = leg['terms'][-1]['party']
    return handle2party
