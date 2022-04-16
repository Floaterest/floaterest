import requests, re, os
from argparse import ArgumentParser

USER = 'floaterest'
URL = 'https://github-readme-streak-stats.herokuapp.com/?user=%s&type=json'

def main(path:str):
    # get current and longest
    with requests.get(URL % USER) as res:
        res.raise_for_status()
        data = res.json()
        longest = data['longestStreak']['length']
        current = data['currentStreak']['length']
    # write svg file
    src = os.path.join('/metrics_renders', path)
    with open(src, 'r') as fi, open(path, 'w') as fo:
        t = fi.read()
        t = re.sub(r'Current streak \d+ days', f'Current streak {current} days', t)
        t = re.sub(r'Best streak \d+ days', f'Best streak {longest} days', t)
        fo.write(t)
    # log
    print(
        'wrote', src, '-->', path,
        'with current streak', current, 'days and'
        'longest streak', longest, 'days'
    )

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('path', type=str, help='path to svg')
    main(parser.parse_args().path)