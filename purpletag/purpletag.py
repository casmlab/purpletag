#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
usage: purpletag [--help] <command> [<args>...]

The most commonly used purpletag commands are:
     collect    Collect tweets from members of congress, stored in json
     parse      Parse tweet json
     score      Create score files containing polarization scores for hashtags and MOCs.
     serve      Launch a web service to visualize results.
See 'purpletag help <command>' for more information on a specific command.

"""

from subprocess import call

from docopt import docopt

CMDS = ['collect', 'parse', 'score', 'serve']


def main():
    args = docopt(__doc__,
                  version='purpletag version 0.1.0',
                  options_first=True)

    argv = [args['<command>']] + args['<args>']
    if args['<command>'] in CMDS:
        exit(call(['purpletag-%s' % args['<command>']] + argv))
    elif args['<command>'] in ['help', None]:
        exit(call(['purpletag', '--help']))
    else:
        exit("%r is not a purpletag command. See 'purpletag help'." % args['<command>'])


if __name__ == '__main__':
    main()
