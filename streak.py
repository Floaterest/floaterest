#!/usr/bin/python3

import argparse
import functools
import itertools
import json
from datetime import datetime

import requests


def http_post(query: str, fields: list, token: str) -> list:
    kwargs = dict(
        url='https://api.github.com/graphql',
        headers={'Authorization': f'bearer {token}'},
        data=json.dumps({'query': query})
    )
    with requests.post(**kwargs) as res:
        res.raise_for_status()
        return functools.reduce(lambda acc, cur: acc[cur], fields, res.json())


def dates(post):
    year = datetime.utcnow().year
    user = post('{ viewer { login } }', ['data', 'viewer', 'login'])
    query = '''{
        user(login: "%s"){
            contributionsCollection(from: "%s"){
                contributionCalendar {
                    weeks { contributionDays { date contributionCount } }
                }
            }
        }
    }'''
    while True:
        weeks = post(query % (user, datetime(year, 1, 1).isoformat()), [
            'data', 'user', 'contributionsCollection',
            'contributionCalendar', 'weeks'
        ])
        contributions = [
            (day['date'], day['contributionCount']) for day in
            itertools.chain(*map(lambda s: s['contributionDays'], weeks))
        ]
        if any(count for _, count in contributions):
            yield contributions
        else:
            return
        year -= 1


def main(token: str) -> int:
    # ah yes, totally readable
    return max(len(list(group)) for label, group in itertools.groupby(
        bool(c) for _, c in sorted(list(itertools.chain(*dates(
            functools.partial(http_post, token=token)
        ))))
    ) if label)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get longest streak')
    parser.add_argument('token', help='Personal Access Token from GitHub')
    print(main(parser.parse_args().token))
