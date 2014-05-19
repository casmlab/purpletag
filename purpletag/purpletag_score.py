"""usage: purpletag score [options]

Compute polarity scores for all .tags files that we haven't yet processed.

Options
    -h, --help             help
    -r, --refresh-mocs     fetch latest legislator information from GovTrack
    -c, --counts           use hashtag count features instead of binary features
    -o, --overwrite        overwrite existing .scores files
"""
from docopt import docopt
import io

import numpy as np
from scipy.sparse import csr_matrix
from scipy.stats.mstats import zscore
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import chi2
from sklearn.preprocessing import LabelEncoder
import requests

from . import config
from data import get_basenames, get_files, twitter_handle_to_party


def has_score_file(tag_file, score_files_bn):
    """ Return true if tag_file has a corresponding score_file. """
    bn = get_basenames([tag_file])[0]
    return bn in score_files_bn


def parse_tags(parts, args):
    """ Parse a line of a .tags file into a dict from tag to count.
    >>> sorted(parse_tags(['foo:10', 'bar:5'], {'--counts':True}).items())
    [('bar', 5.0), ('foo', 10.0)]
    >>> sorted(parse_tags(['foo:10', 'bar:5'], {'--counts':False}).items())
    [('bar', 1.0), ('foo', 1.0)]
    """
    tags = {}
    for t in parts:
        tag_val = t.split(':')
        if not args['--counts']:
            tag_val[1] = 1.
        tags[tag_val[0]] = float(tag_val[1])
    return tags


def parse_tag_file(tag_file, handle2party, args):
    """ Return list of twitter handles, tag counts, and labels. """
    inf = io.open(tag_file, mode='rt', encoding='utf8')
    labels = []
    dicts = []
    handles = []
    for line in inf:
        parts = line.strip().split()
        handle = parts[0]
        if handle in handle2party:
            labels.append(handle2party[handle])
            dicts.append(parse_tags(parts[1:], args))
            handles.append(handle)
    return (handles, dicts, labels)


def feat_counts(fi, ci, X, y):
    """
    Count the number of times feature fi occurs in a row with class ci.

    >>> feat_counts(0, 0, csr_matrix([[0], [1], [0], [1]]), [0, 1, 0, 0])
    1
    >>> feat_counts(0, 1, csr_matrix([[0], [1], [0], [1]]), [0, 1, 0, 1])
    2
    """
    indices = [idx for idx, val in enumerate(y) if val == ci]
    return X[indices][:, fi].sum()


def feat_class_pr(X, y, ci, V):
   return (1. + np.array([feat_counts(i, ci, X, y) for i in range(V)])) \
       / (V + len([yi for yi in y if yi == ci]))


def compute_signs(X, y, V):
    """ For each feature, return 1 if correlated with class 1, else return -1.
    >>> compute_signs(csr_matrix([[1, 0], [1, 0], [0, 1], [0, 1]]), [1, 1, 0, 0], 2)
    [1.0, -1.0]
    """
    pr0 = feat_class_pr(X, y, 0, V)
    pr1 = feat_class_pr(X, y, 1, V)
    return [1. if p1 > p0 else -1. for p0, p1 in zip(pr0, pr1)]


def score_features(X, y, V, args):
    """ FIXME: allow different options. """
    chis, pvals = chi2(X, y)
    # chis /= sum(chis)
    signs = compute_signs(X, y, V)
    signs = np.multiply(chis, signs)
    return signs
    # return zscore(signs)


def write_scores(scores, vocab, tag_file):
    basename = get_basenames([tag_file])[0]
    fp = io.open(config.get('data',
                            'path') + '/' + config.get('data', 'scores') + '/' + basename + '.scores',
                 mode='wt', encoding='utf8')
    for word, score in sorted(zip(vocab, scores), key=lambda x: x[1]):
        fp.write('%s %g\n' % (word, score))
    fp.close()


def score(tag_file, handle2party, args):
    """ Output a file with hashtag scores. """
    handles, tags, parties = parse_tag_file(tag_file, handle2party, args)
    if len(tags) == 0:
        print "can't find any legislators in %s" % tag_file
        return

    vec = DictVectorizer()
    X = vec.fit_transform(tags)
    print '5 features:', vec.get_feature_names()[:5]
    label_enc = LabelEncoder()
    y = label_enc.fit_transform(parties)
    print 'vectorized %d instances' % len(y)
    print 'classes=', label_enc.classes_
    scores = score_features(X, y, len(vec.vocabulary_), args)
    write_scores(scores, vec.get_feature_names(), tag_file)


def get_tag_files(overwrite):
    """ Get .tags files. """
    tag_files = get_files('tags', 'tags')
    if overwrite:
        return tag_files
    else:
        score_files_bn = get_basenames(get_files('scores', 'scores'))
        return [f for f in tag_files if not has_score_file(f, score_files_bn)]


def fetch_legislators():
    """ Download yaml of legislator info from GovTrack. """
    text = requests.get(config.get('govtrack', 'legislators')).text
    fp = io.open(config.get('data', 'path') + '/' + config.get('data', 'leg_yaml'), mode='wt', encoding='utf8')
    fp.write(text)
    fp.close()


def main():
    args = docopt(__doc__)
    if args['--refresh-mocs']:
        print 'refreshing MOCs'
        fetch_legislators()
    print 'reading twitter handles'
    handle2party = twitter_handle_to_party()
    print handle2party.items()[0]
    tag_files = get_tag_files(args['--overwrite'])
    for tag_file in tag_files:
        print 'scoring', tag_file
        score(tag_file, handle2party, args)


if __name__ == '__main__':
    main()
