# coding=utf-8
"""
Organize commits between each tag

:author: Andrew B Godbehere
:date: 4/21/16
"""

import git
import re
from textwrap import dedent
import argparse

LABELS = {'#new', '#change', '#bug', '#test', '#doc', '#depr', '#minor', '#ignore'}


def format_markdown(report):
    mdtext = ""
    for note in report:
        mdtext += "# {}\n\n".format(note['tag'])

        if note['#new']:
            mdtext += "## NEW\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['#new']])
            mdtext += '\n\n'

        if note['#change']:
            mdtext += "## CHANGE\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['#change']])
            mdtext += '\n\n'

        if note['#bug']:
            mdtext += "## BUGFIX\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['#bug']])
            mdtext += '\n\n'

        if note['#test']:
            mdtext += "## TEST/DEPLOY\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['#test']])
            mdtext += '\n\n'

        if note['#doc']:
            mdtext += "## DOCUMENTATION\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['#doc']])
            mdtext += '\n\n'

        if note['#depr']:
            mdtext += "## DEPRECATED\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['#depr']])
            mdtext += '\n\n'

        if note['general']:
            mdtext += "## GENERAL\n"
            mdtext += '\n'.join(["    * {}".format(s) for s in note['general']])
            mdtext += "\n\n-----\n\n"
    return mdtext


def get_tag_ranges(repo):
    result = repo.git.for_each_ref('refs/tags', sort='taggerdate', format='%(refname) %(taggerdate)')
    print(result)
    tags = []
    for line in result.splitlines():
        elements = line.split()
        if len(elements) > 1:   # has timestamp, so use the tag
            tags.append(elements[0].split('/')[-1])   # actual tag name

    tags.append("HEAD")
    print("TAGS: {}".format(tags))
    reversed_ranges = ['{0}..{1}'.format(tags[i - 1], tags[i]) for i in reversed(range(1, len(tags)))]
    return reversed_ranges


def get_contributors(repo):
    """
    Also sort by number of contributions
    :param repo:
    :return:
    """
    pass


def parse_commits(repo, r, left_only=False):
    label_finder = re.compile(r'({})\b'.format('|'.join(l for l in LABELS)), re.IGNORECASE)
    try:
        tag = r.split('..')[1]
    except IndexError:
        tag = r
    else:
        if tag == "HEAD":
            tag = "UNRELEASED"
    release_note = {'tag': tag, 'general': []}
    release_note.update({k: [] for k in LABELS})
    if left_only:
        rawdata = repo.git.log(r, pretty="format:%s", no_decorate=True, left_only=True)
    else:
        rawdata = repo.git.log(r, pretty="format:%s", no_decorate=True, left_right=True)
    for line in rawdata.splitlines():
        labels = set(label_finder.findall(line)) & LABELS
        if '#minor' in labels or '#ignore' in labels:
            continue
        updated_line = label_finder.sub('', line)
        updated_line = ' '.join(updated_line.split())  # normalize whitespaces
        if not labels:
            release_note['general'].append(updated_line)
        else:
            for l in labels:
                release_note[l].append(updated_line)
    return release_note


def group_by_tag(repo):
    ranges = get_tag_ranges(repo)
    #print("RANGES: {}".format(ranges))
    # latest_tag = ranges[0].split('..')[1]
    first_tag = ranges[-1].split('..')[0]
    #ranges = [latest_tag + '..HEAD'] + ranges
    release_notes = []

    for r in ranges:
        release_notes.append(parse_commits(repo, r))
        # for rn in release_notes:
        #    print(rn)
    release_notes.append(parse_commits(repo, first_tag, left_only=True))  # one-sided inclusion
    return release_notes

def group_by_contributor(repo):
    pass  #contributors =

def get_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--tag", "-t", action='store_true')
    group.add_argument('--date', '-d', choices=['y', 'q', 'm', 'w', 'd', 'h'])
    group.add_argument('--contributor', '-c', action='store_true')
    parser.add_argument("--console", '-p', action='store_true')
    args = parser.parse_args()
    return args

def run():
    args = get_args()

    repo = git.Repo(".")  # current directory

    if args.tag:
        release_notes = group_by_tag(repo)
    elif args.contributor:
        release_notes = []
    elif args.date is not None:
        release_notes = []
    else:
        # DEFAULT ACTION HERE
        release_notes = group_by_tag(repo)

    if args.console:
        print(format_markdown(release_notes))
    else:
        with open("RELEASE_NOTES.md", 'w') as outfile:
            outfile.write(format_markdown(release_notes))


if __name__ == "__main__":
    run()
