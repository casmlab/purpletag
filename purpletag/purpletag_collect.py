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
import time
import requests

from TwitterAPI import TwitterAPI

from . import config
from data import parse_twitter_handles


def fetch_twitter_handles():
    # FIXME: Test
    print 'TEST FETCH_TWITTER_HANDLES'
    text = requests.get(config.get('govtrack', 'handles')).text
    fp = open(config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml'), 'w')
    fp.write(text)
    fp.close()


def make_output_file():
    return config.get('data', 'path') + '/' + config.get('data', 'jsons') + '/' + str(int(time.time())) + '.json'


def track_users(ids, api):
    # FIXME: broken
    print 'tracking', len(ids), 'users'
    outf = io.open(make_output_file(), mode='wt', encoding='utf8')
    results = api.request('statuses/filter', {'follow': ','.join(ids)})
    print results.text
    count = 0
    for tweet in results.get_iterator():
        outf.write(json.dumps(tweet))
        outf.write('\n')
        count += 1
        if count > 1000:
            outf.close()
            outf = make_output_file()
            count = 0


def search_users(ids, api):
    """ Use the Twitter REST API to fetch the most recent 3,200 tweets from
    each user in the list of ids. When rate limits are encountered, sleep for
    5 minutes and try again."""
    print 'searching for', len(ids), 'users'
    outf = io.open(make_output_file(), mode='w', encoding='utf8')
    for id_ in ids:
        max_id = None
        print 'searching for', id_
        while True:
            if max_id:
                results = api.request('statuses/user_timeline', {'id': id_, 'count': 200, 'max_id': max_id})
            else:
                results = api.request('statuses/user_timeline', {'id': id_, 'count': 200})
            print '\tstatus:', results.status_code
            tweets = [t for t in results]
            if results.status_code != 200:  # something went wrong
                print 'sleeping on error:', results.text
                time.sleep(300)
            elif len(tweets) == 0:  # on to the next user.
                break
            else:  # save these tweets and update max_id
                outf.write(results.text + '\n')
                max_id = min(t['id'] for t in results) - 1
    outf.close()


def lookup_ids(handles, api):
    """ Fetch the twitter ids of each screen_name. """
    ids = set()
    # for handle_list in [handles[100 * i:100 * i + 100] for i in range(len(handles))]:
    for handle_list in [handles[100 * i:100 * i + 100] for i in range(1)]:
        if len(handle_list) > 0:
            print handle_list
            r = api.request('users/lookup', {'screen_name': ','.join(handle_list)})
            for item in r.get_iterator():
                ids.add(item['id_str'])
    return ids


def main():
    args = docopt(__doc__)
    if args['--refresh-handles']:
        print 'refreshing handles'
        fetch_twitter_handles()
    handle_yaml = parse_twitter_handles()
    handles = [d['social']['twitter'] for d in handle_yaml]
    print 'read', len(handles), 'handles'
    api = TwitterAPI(config.get('twitter', 'consumer_key'),
                     config.get('twitter', 'consumer_secret'),
                     config.get('twitter', 'access_token'),
                     config.get('twitter', 'access_token_secret'))
    ids = lookup_ids(handles, api)
    if args['--track']:
        track_users(ids, api)
    elif args['--search']:
        search_users(ids, api)


if __name__ == '__main__':
    main()
