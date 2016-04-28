#!/usr/bin/env python3
import time
from argparse import ArgumentParser
from collections import defaultdict
from urllib.parse import quote_plus

import requests_unixsocket
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

session = requests_unixsocket.Session()
PREFIX = "uwsgi"
EXCLUDE_FIELDS = {"pid", "uid", "cwd"}
LABEL_VALUE_FIELDS = {"id", "name"}


def object_to_prometheus(prefix, stats_dict, labels, label_name=None):
    label_value = next((stats_dict[field] for field in LABEL_VALUE_FIELDS if field in stats_dict), None)
    if label_name is not None and label_value is not None:
        label_name = label_name.rstrip("s")
        labels = labels + [(label_name, str(label_value))]

    for name, value in stats_dict.items():
        name = name.replace(" ", "_")
        if name.isupper() or name in EXCLUDE_FIELDS:
            # If isupper - it is request vars. No need to save it.
            continue
        if isinstance(value, list):
            yield from list_to_prometheus("{}_{}".format(prefix, name), value, labels, name)
        elif name not in LABEL_VALUE_FIELDS and isinstance(value, (int, float)):
            yield "{}_{}".format(prefix, name), sorted(labels), value


def list_to_prometheus(prefix, stats_list, labels, label_name):
    for stats in stats_list:
        yield from object_to_prometheus(prefix, stats, labels, label_name)


def build_prometheus_stats(stats_addr):
    uwsgi_stats = get_stats(stats_addr)
    stats = object_to_prometheus(PREFIX, uwsgi_stats, [])
    grouped_stats = defaultdict(list)
    # Need to group all values by name, otherwise prometheus do not accept it
    for metric_name, labels, value in stats:
        grouped_stats[metric_name].append((labels, value))
    for metric_name, stats in grouped_stats.items():
        label_names = [name for name, _ in stats[0][0]]
        g = GaugeMetricFamily(metric_name, "", labels=label_names)
        for labels, value in stats:
            g.add_metric([value for _, value in labels], value)
        yield g


def get_stats_collector(stats_getter):
    class StatsCollector:
        def collect(self):
            yield from stats_getter()
    return StatsCollector()


def get_stats(stats_addr):
    resp = session.get(stats_addr)
    resp.raise_for_status()
    return resp.json()


def _parse_args():
    parser = ArgumentParser(description="uwsgi stats prometheus exporter")
    parser.add_argument("-p", "--bind_port", type=int, default=1717)
    parser.add_argument("--bind_address", type=str, default="127.1")
    parser.add_argument("--stats_addr", type=str, required=True)
    return parser, parser.parse_args()


def _main():
    parser, args = _parse_args()
    if args.stats_addr.startswith("http"):
        stats_addr = args.stats_addr
    elif args.stats_addr.startswith("/"):
        stats_addr = "http+unix://{}".format(quote_plus(args.stats_addr))
    elif args.stats_addr.startswith("@"):
        # requests_unixsocket not support this
        parser.error("Abstract namespace unix sockets not supported")
    else:
        stats_addr = "http://{}".format(args.stats_addr)
    REGISTRY.register(get_stats_collector(lambda: build_prometheus_stats(stats_addr)))
    start_http_server(args.bind_port, args.bind_address)
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    _main()
