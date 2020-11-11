# -*- coding: utf-8 -*-
from github import Github
from github.Issue import Issue
import argparse
import os
import glob

TODO_ISSUES_LABELS = ["TODO"]

def get_me(user):
    return user.get_user().login


def isMe(issue, me):
    return issue.user.login == me

def login(token):
    return Github(token)


def get_repo(user: Github, repo: str):
    return user.get_repo(repo)


def save_issue(issue, me, directory='backup'):
    os.makedirs(directory, exist_ok=True)
    fileList = glob.glob(f'{directory}/{issue.number}_*.md')
    for f in fileList:
        try:
            os.remove(f)
        except:
            pass
    name = f"{directory}/{issue.number}_{issue.title.replace(' ', '.')}.md"
    with open(name, "w") as f:
        f.write(f"# [{issue.title}]({issue.html_url})\n\n")
        f.write(issue.body)
        if issue.comments:
            for c in issue.get_comments():
                if isMe(c, me):
                    f.write("\n\n---\n\n")
                    f.write(c.body)


def main(token, repo_name, number):
    user = login(token)
    me = get_me(user)
    repo = get_repo(user, repo_name)
    issue = repo.get_issue(number=number)
    if not isMe(issue, me):
        return
    if issue.labels and issue.labels[0] in TODO_ISSUES_LABELS:
        return
    save_issue(issue, me)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument("number", help="issue_number", type=int)
    options = parser.parse_args()
    main(options.github_token, options.repo_name, options.number)
