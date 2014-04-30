#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import ConfigParser
import glob
import os
from os.path import basename
import sys

__author__ = 'Aron Culotta'
__email__ = 'aronwc@gmail.com'
__version__ = '0.1.0'

config = ConfigParser.RawConfigParser()
config.read(os.environ['PURPLE_CFG'])
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
