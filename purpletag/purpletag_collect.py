"""usage:
    purpletag collect [options]
    purpletag collect (-t | --track | -s | --search) [options]

Options
    -h, --help
    -o, --output <file>        output path
    -r, --refresh-handles      fetch latest twitter handles for politicians
    -t, --track                collect tweets in real time using streaming API
    -s, --search               search historical tweets using search API
"""
from docopt import docopt
import io
import json
import os
import time
import requests
import sys
import traceback

import twutil

from . import config
from data import parse_twitter_handles


def fetch_twitter_handles():
    """ Fetch twitter handles from govtrack. """
    text = requests.get(config.get('govtrack', 'handles')).text
    fp = open(config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml'), 'w')
    fp.write(text)
    fp.close()


def make_output_file():
    return config.get('data', 'path') + '/' + config.get('data', 'jsons') + '/' + str(int(time.time())) + '.json'


def track_users(ids):
    """
    Track users by id, writing to jsons folder.
    """
    print 'tracking', len(ids), 'users'
    outf = io.open(make_output_file(), mode='wt', encoding='utf8')
    count = 0
    for tweet in twutil.collect.track_user_ids(ids):
        try:
            outf.write(json.dumps(tweet, ensure_ascii=False, encoding='utf8'))
            outf.write(u'\n')
            outf.flush()
            count += 1
            if count > 100000:
                outf.close()
                outf = io.open(make_output_file(), mode='wt', encoding='utf8')
                count = 0
        except:
            e = sys.exc_info()
            print 'skipping error', e[0]
            print traceback.format_exc()
            twutil.collect.reinit()
            outf.close()
            track_users(ids)

    outf.close()


def search_users(screen_names):
    """ Use the Twitter REST API to fetch the most recent 3,200 tweets from
    each user in the list of ids. When rate limits are encountered, sleep for
    5 minutes and try again."""
    print 'searching for', len(screen_names), 'users'
    outf = io.open(make_output_file(), mode='w', encoding='utf8')
    for screen_name in screen_names:
        print 'searching for', screen_name
        for tweet in twutil.collect.tweets_for_user(screen_name):
            outf.write(json.dumps(tweet, ensure_ascii=False, encoding='utf8') + '\n')
    outf.close()


def handles_exist():
    """ Do we have the yaml file of twitter handles? """
    yaml_doc = config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml')
    return os.path.isfile(yaml_doc)


def main():
    args = docopt(__doc__)
    if args['--refresh-handles'] or not handles_exist():
        print 'refreshing handles'
        fetch_twitter_handles()
    handle_yaml = parse_twitter_handles()
    handles = [d['social']['twitter'] for d in handle_yaml]
    print 'read', len(handles), 'handles'
    if args['--track']:
        ids = twutil.collect.lookup_ids(handles)
        track_users(ids)
    elif args['--search']:
        search_users(handles)


if __name__ == '__main__':
    main()
