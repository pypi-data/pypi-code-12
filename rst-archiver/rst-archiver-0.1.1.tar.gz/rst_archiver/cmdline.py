import argparse
import os
import sys
import urlparse

import choice
import ctags

from .main import archive_file, archive_url


def find_matching_tags(
    tags_file, query, flags=ctags.TAG_PARTIALMATCH | ctags.TAG_IGNORECASE
):
    def entry_to_dict(entry):
        return {
            'name': entry['name'],
            'path': entry['file'],
            'line_number': entry['lineNumber'],
            'pattern': entry['pattern'],
            'kind': entry['kind'],
        }

    entry = ctags.TagEntry()

    if tags_file.find(entry, query, flags):
        yield entry_to_dict(entry)

        while tags_file.findNext(entry):
            yield entry_to_dict(entry)


def get_tag_path(tags_file_path, tag):
    matching_tags = {}

    tags_file = ctags.CTags(tags_file_path)
    for data in find_matching_tags(tags_file, tag):
        matching_tags[data['name']] = data['path']

    if len(matching_tags) == 0:
        raise ValueError(
            "No tag matching \"{name}\" found.".format(
                name=tag,
            )
        )
    elif len(matching_tags) == 1:
        return matching_tags.values()[0]
    else:
        selected = choice.Menu(matching_tags.keys()).ask()
        return matching_tags[selected]


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument('tag')
    parser.add_argument('asset_path')
    parser.add_argument(
        '--tags-file',
        '-t',
        default=os.environ.get('ARCHIVER_TAGS_FILE', ''),
        type=str
    )
    args = parser.parse_args(args)

    document_path = get_tag_path(args.tags_file, args.tag)
    if not os.path.isfile(args.tags_file):
        parser.error(
            'No tags file found at {path}'.format(path=args.tags_file)
        )

    asset_path = args.asset_path
    is_url = bool(urlparse.urlparse(asset_path).scheme)
    if not os.path.isfile(args.asset_path) and not is_url:
        parser.error(
            'File not found at {path}'.format(path=args.asset_path)
        )
    elif not is_url:
        asset_path = os.path.abspath(os.path.expanduser(asset_path))

        archive_file(
            document_path,
            asset_path,
        )
    else:
        archive_url(
            document_path,
            asset_path,
        )
