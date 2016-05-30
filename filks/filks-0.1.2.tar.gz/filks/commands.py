import argparse
from filks.cmudict import CmuDict
from filks.corpus import Corpus
from filks.format_selector import select_format


NLTK_PACKAGES = [
    'brown', 'cmudict', 'treebank',
    'punkt', 'hmm_treebank_pos_tagger', 'maxent_treebank_pos_tagger',
    'universal_tagset',
    #'all',
]


def make_parser():
    parser = argparse.ArgumentParser(description='Filk generator')
    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True

    install_parser = subparsers.add_parser(
        'install', help='Install required NLTK data. May require superuser privileges.')
    install_parser.set_defaults(handler=do_install)
    install_parser.add_argument(
        'packages', nargs='*', default=NLTK_PACKAGES, help='NLTK packages to download')

    format_parser = subparsers.add_parser(
        'format', help='Fill a filk format with words drawn from a text')
    format_parser.add_argument('format', nargs='?', help='Format to fill in filks')

    format_parser.add_argument(
        '--dictionary', '-D',
        help='File to use, as CMU-Dict compatible dictionary'
    )
    format_parser.add_argument(
        '--corpus', '-C',
        help=(
            'Text corpus to draw words from, tagged similarly to Brown corpus.' +
            ' If not provided, you must have run `install` to use the NLTK-downloaded Brown corpus.'
        ),
    )
    format_parser.add_argument(
        '--syllables', '-S',
        default=False,
        action='store_true',
        help='Match syllable counts if possible'
    )
    format_parser.add_argument(
        '--number', '-N',
        type=int, default=1,
        help='Number of results to generate'
    )
    format_parser.set_defaults(handler=do_format)

    return parser


def do_install(args):
    import nltk
    nltk.download(args.packages)


def do_format(args):
    dictionary = CmuDict(args.dictionary)
    corpus = Corpus(args.corpus)
    format = select_format(args.format)

    for i in range(args.number):
        if i:
            print('')  # Just a newline
        print(corpus.random_text(dictionary, syllables=args.syllables).format(format))


def main():
    parser = make_parser()
    args = parser.parse_args()
    args.handler(args)


if __name__ == '__main__':
    main()
