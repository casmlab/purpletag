# purpletag

A tool to track polarized hashtags used by members of the U.S. congress.

## Install

`pip install purpletag`

or, from source:

```
git clone https://github.com/casmlab/purpletag.git
cd purpletag
python setup.py install
```

## Configuration

purpletag depends on [twutil](https://github.com/tapilab/twutil) for
collecting data from Twitter. You'll need to put your credentials in the
following environmental variables:

- `TW_CONSUMER_KEY`
- `TW_CONSUMER_SECRET`
- `TW_ACCESS_TOKEN`
- `TW_ACCESS_TOKEN_SECRET`

purpletag also depends on a configuration file (see [`sample.cfg`](sample.cfg)
for an example). By default, it is assumed to be in `~/.purpletag`, but you
can specify a custom location by setting the `PURPLE_CFG` environmental
variable.

By default, all data will be written to `/data/purpletag`, but you can change
this in the config file.

purpletag fetches the list of legislators and their Twitter handles from
<http://www.govtrack.us/>; these URLs are also specified in the config.


## Getting started

purpletag consists of a number of command-line tools to collect, parse, and
analyze tweets sent by members of Congress.

To see the list of commands:

```
$ purpletag -h
usage: purpletag [--help] <command> [<args>...]

The most commonly used purpletag commands are:
     collect    Collect tweets from members of congress, stored in json
     parse      Parse tweet json
     score      Create score files containing polarization scores for hashtags and MOCs.
See 'purpletag help <command>' for more information on a specific command.
```

### `collect`

This command will fetch tweets from all members of congress listed in `twitter.yaml`.

```
purpletag collect -h
usage:
    purpletag collect [options]
    purpletag collect (-t | --track | -s | --search) [options]

Options
    -h, --help
    -o, --output <file>        output path
    -r, --refresh-handles      fetch latest twitter handles for politicians
    -t, --track                collect tweets in real time using streaming API
    -s, --search               search historical tweets using search API
```

There are two modes of operation:

- `track`: Use the Twitter Streaming API to collect tweets in real-time.
- `search`: Use the Twitter REST API to collect the most recent 3,200 tweets from each legislator.

Output is stored in `/data/purpletag/jsons`.

You probably want to use `search` to first collect all historical tweets, then
run `track` to collect all tweets going forward. **Note:** `search` will take
a long time to run (hours), since the script sleeps to wait out the rate
limits imposed by the REST API.


### `parse`

This command will parse all the collected tweets in `/data/purpletag/jsons`
and extract the hashtags used by each legislator.

```
purpletag parse -h
usage: purpletag parse [options]

Parse .json files into .tags files.

Options
    -h, --help                 help
    -t <timespans>             sliding window timespans [default: 1,30,365]
```

The output looks like this:

```
markwarner whistleblowers:1 studentdebt:1 nova:1 f22:1
repwestmoreland jobs:1 nationaldayofprayer:2 benghazi:3
```

For example, this indicates that Lynn Westmoreland used the hashtag #jobs
once, #nationaldayofprayer twice, and #benghazi three times.

The `-t` parameter indicates a list of timespans to use when aggregating these
statistics. For example `purpletag parse -t 365` will collect all tweets
posted in the past 365 days and compute output like the example above. The
file name itself will indicate this. For example, `2014-05-02.365.tags` is a
tags file created when running this command on May 2, 2014, collecting
statistics for the past 365 days.


### `score`

This command scores hashtags according to their polarity.

```
purpletag score -h
usage: purpletag score [options]

Compute polarity scores for all .tags files that we haven't yet processed.

Options
    -h, --help             help
    -r, --refresh-mocs     fetch latest legislator information from GovTrack
    -c, --counts           use hashtag count features instead of binary features
    -o, --overwrite        overwrite existing .scores files
```

These produce `.scores` files, one per `.tags` file. E.g.,
`2014-05-02.365.scores` contains the scores for the hashtags used for the 365
days prior to May 2, 2014. The scores range from -1 (liberal) to +1
(conservative).

```
demandavote -0.004258
getcovered -0.003548
raisethewage -0.003548
.
.
.
senatemustact 0.001499
fairnessforall 0.001799
tcot 0.002249
```


