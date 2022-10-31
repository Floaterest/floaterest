#!/usr/bin/python3

import argparse
import functools
import itertools
import json
from datetime import datetime

import requests

QUERY = '''{
    user(login: "%s"){
        contributionsCollection(from: "%s"){
            contributionCalendar {
                weeks { contributionDays { date contributionCount } }
            }
        }
    }
}'''


def http_post(query: str, fields: list, token: str) -> list:
    headers = {'Authorization': f'bearer {token}'}
    kwargs = dict(headers=headers, data=json.dumps({'query': query}))
    with requests.post(url='https://api.github.com/graphql', **kwargs) as res:
        res.raise_for_status()
        return functools.reduce(lambda acc, cur: acc[cur], fields, res.json())


def dates(post):
    """Get contributions year by year from most recent"""
    year = datetime.utcnow().year + 1
    user = post('{ viewer { login } }', ['data', 'viewer', 'login'])
    while year := year - 1:
        weeks = post(QUERY % (user, datetime(year, 1, 1).isoformat()), [
            'data', 'user', 'contributionsCollection',
            'contributionCalendar', 'weeks'
        ])
        days = itertools.chain(*map(lambda s: s['contributionDays'], weeks))
        contributions = [(d['date'], d['contributionCount']) for d in days]
        if any(count for _, count in contributions):
            yield contributions
        else:
            return


def main(token: str) -> int:
    # ah yes, totally readable
    post = functools.partial(http_post, token=token)
    return max(len(list(group)) for label, group in itertools.groupby(
        bool(c) for _, c in sorted(list(itertools.chain(*dates(post))))
    ) if label)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get longest streak')
    parser.add_argument('token', help='Personal Access Token from GitHub')
    print(main(parser.parse_args().token))
