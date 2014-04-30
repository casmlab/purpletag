"""usage: purpletag collect [options]

Options
    -h, --help
    -o, --output <file>        output path
    -r, --refresh-handles      fetch latest twitter handles for politicians
"""
from docopt import docopt
import io
import time
import requests

from TwitterAPI import TwitterAPI

from . import config
from data import parse_twitter_handles


def fetch_twitter_handles():
    # FIXME: Test
    print 'TEST FETCH_TWITTER_HANDLES'
    text = requests.get(config.get(config.get('govtrack', 'handles'))).text
    fp = open(config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml'), 'w')
    fp.write(text)
    fp.close()


def make_output_file():
    return config.get('data', 'path') + '/' + config.get('data', 'jsons') + '/' + str(int(time.time())) + '.json'


def track_users(ids, api):
    print 'tracking', len(ids), 'users'
    outf = io.open(make_output_file(), mode='wt', encoding='utf8')
    results = api.request('statuses/filter', {'follow': ','.join(ids)})
    print results.text
    count = 0
    for tweet in results.get_iterator():
        outf.write(tweet)
        outf.write('\n')
        count += 1
        if count > 1000:
            outf.close()
            outf = make_output_file()
            count = 0


def lookup_ids(handles, api):
    """ Fetch the twitter ids of each screen_name. """
    ids = set()
    for handle_list in [handles[100 * i:100 * i + 100] for i in range(len(handles))]:
        if len(handle_list) > 0:
            print handle_list
            r = api.request('users/lookup', {'screen_name': ','.join(handle_list)})
            for item in r.get_iterator():
                ids.add(item['id_str'])
    return ids


def main():
    args = docopt(__doc__)
    print args
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
    track_users(ids, api)


if __name__ == '__main__':
    main()
