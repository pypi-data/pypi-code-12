import sys
import argparse

from .client import FFWD
from .samples import Metric, Event


def tag_type(s):
    """
    Parse a tag.
    """

    parts = s.split(':', 1)

    if len(parts) < 2:
        raise argparse.ArgumentTypeError('Not a tag (<key>:<value>)')

    return (parts[0], parts[1])


def send_metric(ns):
    tags = dict(ns.tags)
    ns.ffwd.metric(ns.key, **tags).send(ns.value)


def send_event(ns):
    tags = dict(ns.tags)
    ns.ffwd.event(ns.key, **tags).send()


parser = argparse.ArgumentParser()
sub = parser.add_subparsers()


metric = sub.add_parser('metric', help='Send a Metric')
metric.add_argument('-t', dest='tags', metavar="<key>:<value>",
                    help="Add a tag", type=tag_type, default=[],
                    action='append')
metric.add_argument('-k', dest='key', metavar="<key>",
                    help="Key to use (default: ffwd-send)",
                    default="ffwd-send")
metric.add_argument('value', metavar="<number>",
                    help="Add a tag", type=float)
metric.set_defaults(action=send_metric)


event = sub.add_parser('event', help='Send an Event')
event.add_argument('-t', dest='tags', help="Add a tag", type=tag_type)
event.add_argument('-k', dest='key', metavar="<key>",
                   help="Key to use (default: ffwd-send)",
                   default="ffwd-send")
event.set_defaults(action=send_event)


def entry():
    """
    Entry-point to ffwd-send.
    """
    ns = parser.parse_args()
    ns.ffwd = FFWD()
    ns.action(ns)
    sys.exit(0)
