"""usage: purpletag score [options]

Compute polarity scores for all .tags files that we haven't yet processed.

Options
    -h, --help             help
    -r, --refresh-mocs     fetch latest legislator information from GovTrack
"""

from docopt import docopt
import io
import requests

from sklearn.feature_extraction import DictVectorizer

from . import config
from data import get_basenames, get_files, parse_legislators, parse_twitter_handles


def has_score_file(tag_file, score_files_bn):
    """ Return true if tag_file has a corresponding score_file. """
    bn = get_basenames([tag_file])[0]
    return bn in score_files_bn


def parse_tag_file(tag_file, handle2party):
    """ Return list of twitter handles, tag counts, and labels. """
    inf = io.open(tag_file, mode='rt', encoding='utf8')
    labels = []
    dicts = []
    handles = []
    for line in inf:
        parts = line.strip().split()
        handle = parts[0]
        tags = dict([(t.split(':')[0], t.split(':')[1]) for t in parts[1:]])
        if handle in handle2party:
            labels.append(handle2party[handle])
            dicts.append(tags)
            handles.append(handle)
    return (handles, dicts, labels)


def score(tag_file, handle2party):
    """ Output a file with hashtag scores. """
    handles, tags, parties = parse_tag_file(tag_file, handle2party)
    if len(tags) == 0:
        raise ValueError("can't find any legislators in .tags files. Perhaps the legislator yaml file is bad?")

    print tags[0]
    vec = DictVectorizer()
    X = vec.fit_transform(tags)
    print X[0]
    print vec.vocabulary_
    # FIXME: Finish this by scoring each hashtag.


def get_tag_files():
    """ Get .tags files. """
    tag_files = get_files('tags', 'tags')
    score_files_bn = get_basenames(get_files('scores', 'scores'))
    return [f for f in tag_files if not has_score_file(f, score_files_bn)]


def fetch_legislators():
    """ Download yaml of legislator info from GovTrack. """
    text = requests.get(config.get('govtrack', 'legislators')).text
    fp = io.open(config.get('data', 'path') + '/' + config.get('data', 'leg_yaml'), mode='wt', encoding='utf8')
    fp.write(text)
    fp.close()


def twitter_handle_to_party():
    """ Read YAML files from GovTrack and map twitter handle to party. We
    restrict to Republican/Democrat.
    FIXME: This assumes bioguide ids always exist. We also assume that the party of your last term is your party.
    """
    twitter_handles = parse_twitter_handles()
    bioguide2handle = dict([(t['id']['bioguide'], t['social']['twitter']) for t in twitter_handles])
    legislators = parse_legislators()
    handle2party = dict()
    for leg in legislators:
        if leg['id']['bioguide'] in bioguide2handle:
            party = leg['terms'][0]['party']
            if party in ['Republican', 'Democrat']:
                handle2party[bioguide2handle[leg['id']['bioguide']]] = leg['terms'][-1]['party']
    return handle2party


def main():
    args = docopt(__doc__)
    print args
    if args['--refresh-mocs']:
        print 'refreshing MOCs'
        fetch_legislators()
    handle2party = twitter_handle_to_party()
    print handle2party.items()[0]
    tag_files = get_tag_files()
    for tag_file in tag_files:
        print 'scoring', tag_file
        score(tag_file, handle2party)

if __name__ == '__main__':
    main()
