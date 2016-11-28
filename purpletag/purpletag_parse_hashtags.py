import os
import pandas as pd
import yaml
import configparser

# generate a list of legislators that have twitter handles
def parse_twitter_handles(config):
    yaml_doc_path = config.get('data', 'path') + '/' + config.get('data', 'twitter_yaml')
    if not os.path.isfile(yaml_doc_path):
        fetch_twitter_handles()
    yaml_doc = yaml.load(open(yaml_doc_path, 'r'))
    return [d for d in yaml_doc if 'twitter' in d['social']]

# create a dict where the key is the date and the value is a 
# list of lists [[hashtag, score],[hashtag, score],...] for that day
def parse_hashtag_scores(config, score_files):
    moc_scores = {}
    for f in score_files:
        score_path = config.get('data', 'path') + '/' + config.get('data', 'scores') + '/' + f
        # only looks at one day at a time - future update could make this configurable
        if '.1.scores' in f:
            components = f.split('.')
            date = components[0]
            with open(score_path) as score_file:
                scores = score_file.readlines()
            moc_scores[date] = scores
    return moc_scores

# create a dict of scores for each legislator
# on each date for which scores are available
def read_scores(legislators, scores):
    leg_scores = {}
    for l in legislators:
        handle = l['social']['twitter'].lower()
        leg_scores[handle] = {}

    for date in scores:
        for score_item in scores[date]:
            handle, score = score_item.split()
            leg_scores[handle][date] = score
    return leg_scores

def main():
	config = configparser.ConfigParser()
	config.read('settings.cfg')
	score_path = config.get('data', 'path') + '/' + config.get('data', 'scores') + '/'
	score_files = os.listdir(score_path)
	moc_scores = parse_moc_scores(config, score_files)
	mocs_with_twitter = parse_twitter_handles(config)
	moc_scores_by_date = read_scores(mocs_with_twitter, moc_scores)
	df = pd.DataFrame(dict([(k, pd.Series(v)) for k,v in moc_scores_by_date.items()])).transpose().dropna(how='all')
	data_file = config.get('data', 'path') + '/' + config.get('data', 'moc_scores')
	df.to_csv(data_file, sep='\t')


if __name__ == "__main__":
	main()