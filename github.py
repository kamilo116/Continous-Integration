"""
Skrypt zwiera wszystkie funkcje potrzebne do pobrania danych z danego <REPOZYTORIUM>, uzytkownika <USER> z github.com

W celu autoryzacji wymagane jest wczesniejsze wygenerowanie tokena w github.com,
by moc zdalnie logowac sie do repozytorium.
"""

import requests
import json
import re

HISTORY_FILE = "commits_history.txt"


class GitConnectionError(Exception): pass


def format_date(commit_date):

    commit_date = re.findall(r'\d+', commit_date)
    return commit_date[:3]


def create_github_session(token):

    s = requests.Session()
    g = s.get('https://api.github.com/user', headers={"Authorization": "token " + token})
    if '200' in g.headers['Status']:
        return s
    else:
        raise GitConnectionError


def get_get_dates_of_all_commits_from_github(session, username, repository, token):

    commits = session.get('https://api.github.com/repos/' + username + '/'+repository+'/commits',
                          headers={"Authorization": "token " + token})
    all_commit_dates = []
    commits_json_data = json.loads(commits.text)
    for next_commit in commits_json_data:
        all_commit_dates.append(next_commit['commit']['author']['date'])
    return all_commit_dates


def is_newer_commit(all_commit_dates) -> bool:

    with open(HISTORY_FILE, 'r') as f:
        last_commit_date = f.readline()
        print("INFO: Last remembered commit's date: ", last_commit_date)
        all_commit_dates = list(filter(lambda d: d > last_commit_date, all_commit_dates))
        try:
            last_commit_date = all_commit_dates[0]
            print("INFO: After {0} was new commit: {1}".format(last_commit_date, last_commit_date))
            with open(HISTORY_FILE, 'w') as f:
                f.write(last_commit_date + '\n')
            return True
        except IndexError:
            print("There hasn't been any commits since: ", last_commit_date)
            # print("WARNING: There hasn't been any commits since ", last_commit_date)
        return False
