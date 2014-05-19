"""usage: purpletag serve [options]

Launch a web service to visualize results.

Options
    -h, --help             help
    -n <tags>              number of tags to show from each party [default: 100]
"""
from collections import defaultdict
import io
import os
from pkg_resources import resource_string
import SimpleHTTPServer
import SocketServer

from docopt import docopt
import numpy as np

from . import config
from data import get_basenames, get_files


def parse_filename(score_file):
    base = get_basenames([score_file])[0]
    return base.split('.')


def read_scores(score_file, n):
    """ Return dict from hashtag to score in this file. Assumes that the file
    is already sorted in decreasing order. """
    inf = io.open(score_file, mode='rt', encoding='utf8')
    d = {}
    for line in inf:
        tag, score = line.strip().split()
        d[tag] = float(score)
    tags = np.array(d.keys())
    vals = np.array([d[t] for t in tags])
    indices = np.argsort(vals)
    result = defaultdict(lambda: 'NaN')
    m = min(n, len(tags))

    for i, idx in enumerate(indices[:m]):
        result[tags[idx]] = unicode(-(m - i))
    for i, idx in enumerate(indices[::-1][:m]):
        result[tags[idx]] = unicode(m - i)
    print result
    return result

    # tags_to_keep = set(tags[np.argsort(vals)[range(m) + range(len(tags) - m, len(tags))]])
    # for tag in tags_to_keep:
    #     result[tag] = unicode(d[tag])
    # return result


def load_scores(n=20):
    """ Create a csv file containing the ranks for the top n hashtags, according to the .scores files.
    n ... number of top/bottom ranked hashtags to include.
    """
    # ranks: spans -> day -> tag -> score. E.g., 30 -> 2014-05-09 -> obamacare -> 10.5
    result = defaultdict(lambda: {})
    for score_file in get_files('scores', 'scores'):
        print score_file
        day, timespan = parse_filename(score_file)
        scores = read_scores(score_file, n)
        result[timespan][day] = scores
    return result


def write_scores(scores):
    """ Write date/tag/score CSV files to be read by web app."""
    for timespan in scores:
        fp = io.open(config.get('data', 'path') + '/' + config.get('data', 'web') + '/' +
                     timespan + '.csv', mode='wt', encoding='utf8')
        days = sorted(scores[timespan])
        all_tags = set()
        for day in days:
            all_tags.update(scores[timespan][day])
        fp.write(u'day,%s\n' % ','.join(all_tags))
        for day in days:
            s = ','.join(scores[timespan][day][tag] for tag in all_tags)
            fp.write(u'%s,%s\n' % (day, s))
        fp.close()


def serve():
    os.chdir(config.get('data', 'path') + '/' + config.get('data', 'web'))
    port = int(config.get('web', 'port'))
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(("", port), Handler)
    print "serving at port", port
    httpd.serve_forever()


def create_html(scores):
    template_file = unicode(resource_string(__name__, 'web/plot.html'))
    index = io.open(config.get('data', 'path') + '/' + config.get('data', 'web') +
                    '/index.html', mode='wt', encoding='utf8')
    index.write(u'<html>\n')
    for timespan in scores:
        fp = io.open(config.get('data', 'path') + '/' + config.get('data', 'web') + '/' +
                     timespan + '.html', mode='wt', encoding='utf8')
        fp.write(template_file % timespan)
        index.write(u'<a href="%s.html">%s day smoothing</a><br>\n' % (timespan, timespan))
        fp.close()
    index.write(u'</html>\n')
    index.close()


def main():
    args = docopt(__doc__)
    n = int(args['-n'])
    scores = load_scores(n)
    write_scores(scores)
    create_html(scores)
    serve()


if __name__ == '__main__':
    main()
