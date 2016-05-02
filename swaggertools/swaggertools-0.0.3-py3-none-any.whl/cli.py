import argparse
from swaggertools.spec import resolve


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', type=argparse.FileType('r'))
    parser.add_argument('--format',
                        choices={'yaml', 'html'},
                        default='yaml')
    parser.add_argument('--granularity',
                        choices={'compact', 'sparse', 'full'},
                        default='sparse')
    args = parser.parse_args(args)
    return args, parser


def main(args=None):
    args, parser = parse_args(args=None)
    if args.format == 'yaml':
        app = resolve(args.infile, granularity=args.granularity)
        format_yaml(app)
    elif args.format == 'html':
        data = resolve(args.infile, granularity='full')
        format_html(data)


def format_yaml(app):
    print(app.to_yaml(width=79))


def format_html(app):
    raise NotImplementedError()
