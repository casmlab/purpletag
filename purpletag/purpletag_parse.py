"""usage: purpletag parse [options]

Parse .json files into .tags files.

Options
    -h, --help                 help
    -t <timespans>             sliding window timespans [default: 1,30,365]
"""
import codecs
from collections import Counter, defaultdict
from datetime import datetime
import io
import json
import sys
import traceback

from numpy import array as npa
from docopt import docopt

from data import get_files
from . import config

sys.stdout = codecs.getwriter('utf8')(sys.stdout)


def parse_day(s):
    """
    >>> d = parse_day('Mon Apr 01 13:44:45 +0000 2011')
    >>> print d.strftime('%Y-%m-%d')
    2011-04-01
    """
    return datetime.strptime(' '.join(npa(s.split())[[1, 2, 5]]), '%b %d %Y')


def get_hashtags(js):
    """
    >>> get_hashtags({"entities": {"hashtags": [{"indices": [70,81], "text": "bipartisan"}, {"indices": [121, 138], "text": "energyefficiency"}]}})
    ['bipartisan', 'energyefficiency']
    """
    if 'entities' in js and 'hashtags' in js['entities']:
        return [ht['text'].lower() for ht in js['entities']['hashtags']]


def json_iterate(json_fp, ids_seen):
    """ Iterate tweet day, screen_name, and hashtag_list for tweets containing
    hashtags. """
    for line in json_fp:
        try:
            jsons = json.loads(line)
            if type(jsons) is dict:
                jsons = [jsons]
            for js in jsons:
                if not js['id'] in ids_seen:
                    hashtags = get_hashtags(js)
                    if len(hashtags) > 0:
                        sname = js['user']['screen_name'].lower()
                        day = parse_day(js['created_at'])
                        yield (day, sname, hashtags)
                        ids_seen.add(js['id'])
        except:
            e = sys.exc_info()
            print 'skipping', e[0]
            print traceback.format_exc()


def parse(json_f, tags_list, timespans, today, ids_seen):
    """ Populate the tags_list Counters for each timespan. """
    print 'parsing', json_f
    json_fp = io.open(json_f, mode='rt', encoding='utf8')
    for day, sname, hashtags in json_iterate(json_fp, ids_seen):
        days_old = (today - day).days
        print sname, hashtags
        for timespan, tags in zip(timespans, tags_list):
            if days_old <= timespan:
                tags[sname].update(hashtags)
    return tags_list


def write_tags(outfile, tags):
    """ Write tags in format:
    screen_name tag1:count tag2:count ...
    """
    for sn in sorted(tags):
        outfile.write(sn + ' ')
        outfile.write(' '.join('%s:%d' % (x[0], x[1]) for x in sorted(tags[sn].iteritems(), key=lambda x: x[1])))
        outfile.write(u'\n')
    outfile.close()


def parse_timespans(s):
    """
    >>> parse_timespans('50,1,12')
    [50, 12, 1]
    """
    return [int(ts) for ts in sorted(s.split(','), reverse=True)]


def open_outfiles(today, timespans):
    """ Create output file handles for each timespan. """
    today_s = today.strftime('%Y-%m-%d')
    outpath = config.get('data', 'path') + '/' + config.get('data', 'tags')
    return [io.open(outpath + '/' + today_s + '.' + str(span) + '.tags', mode='w', encoding='utf8')
            for span in timespans]


def main():
    args = docopt(__doc__)
    today = datetime.now()
    timespans = parse_timespans(args['-t'])
    tags_list = [defaultdict(lambda: Counter()) for i in range(len(timespans))]
    files = get_files('jsons', 'json')
    ids_seen = set()
    for f in files:
        parse(f, tags_list, timespans, today, ids_seen)

    outfiles = open_outfiles(today, timespans)
    for outfile, tags in zip(outfiles, tags_list):
        write_tags(outfile, tags)


if __name__ == '__main__':
    main()
