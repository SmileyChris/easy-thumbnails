#!/usr/bin/env python
"""
Get a git project's authors (ordered by most contributions).
"""

import re
import six
import subprocess
from operator import itemgetter

re_line = re.compile(six.b(r'(\d+)\s+(\d+)\s+[^<]+$'))
re_author = re.compile(six.b(r'.+<(.+)>$'))


def get_authors(exclude_primary_author=True):
    git_log = subprocess.Popen(
        ["git", "log", "--format=%aN <%aE>", "--numstat"],
        stdout=subprocess.PIPE)

    output = git_log.communicate()[0]

    authors = {}
    author = None
    for line in output.splitlines():
        match = re_line.match(line)
        if not match:
            if line:
                author = line
            continue
        authors[author] = authors.get(author, 0) + max([
            int(num) for num in match.groups()])

    # Combine duplicate authors (by email).
    emails = {}
    for author, changes in list(authors.items()):
        match = re_author.match(author)
        if not match:
            continue
        author_emails = match.group(1)
        for email in author_emails.split(six.b(',')):
            if six.b('@') not in email:
                continue
            if email in emails:
                remove_author = emails[email]
                if remove_author not in authors:
                    continue
                if changes < authors[remove_author]:
                    author, remove_author = remove_author, author
                authors[author] = authors[author] + authors[remove_author]
                del authors[remove_author]
            else:
                emails[email] = author

    # Sort authors list.
    list_authors = sorted(authors.items(), key=itemgetter(1), reverse=True)

    total = float(sum(authors.values()))

    if exclude_primary_author:
        top_author = list_authors.pop(0)
        total -= top_author[1]

    return [
        (author.decode(), changes, changes / total * 100)
        for author, changes in list_authors]


if __name__ == '__main__':
    for author, changes, percent in get_authors():
        print(author)
