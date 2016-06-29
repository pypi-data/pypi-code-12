
import argparse
import itertools
import logging
import os
import os.path as osp
import StringIO
import signal
import sys
import threading
import time

from dnslib import RR,QTYPE,RCODE
from dnslib.server import DNSServer,DNSHandler,BaseResolver,DNSLogger

from .config import (
    DEFAULT_CONFIG_PATH,
    GSDriver,
    GStorageKeybaseProfile,
    Profile,
    Profiles,
)

def config_pull(profile, bucket, identity, **kwargs):
    keybase_id = identity.split("://", 1)
    profile = GStorageKeybaseProfile(profile, GSDriver, bucket, keybase_id, **kwargs)
    profile.pull()

def config_push(profile, bucket, **kwargs):
    """Push encryted configuration of a profile on Google Storage

    :param profile: profile to push (a directory in ~/.config/cloud-dns/)
    :param bucket: the destination Google Storage bucket
    :param config_dir: absolute path to Cloud DNS root config dir
    (default ~/.config/cloud-dns)
    """
    profile = GStorageKeybaseProfile(profile, GSDriver, bucket, **kwargs)
    profile.push()


class ZoneResolver(BaseResolver):
    """
        Simple fixed zone file resolver.
    """

    def __init__(self, zone_file_generator, glob=False, ttl=3600):
        """
            Initialise resolver from zone file.
            Stores RRs as a list of (label,type,rr) tuples
            If 'glob' is True use glob match against zone file
        """
        self.glob = glob
        self.eq = 'matchGlob' if glob else '__eq__'
        self.zone_file_generator = zone_file_generator
        self.load()
        if ttl > 0:
            thread = threading.Thread(target=self.reload, args=(ttl,))
            thread.daemon = True
            thread.start()

    def load(self):
        logging.info("Loading DNS information from cloud providers")
        self.zone = [(rr.rname,QTYPE[rr.rtype],rr) for rr in RR.fromZone(self.zone_file_generator())]

    def reload(self, ttl):
        while True:
            time.sleep(ttl)
            logging.info("Updating DNS information from cloud providers")
            self.load()

    def resolve(self,request,handler):
        """
            Respond to DNS request - parameters are request packet & handler.
            Method is expected to return DNS response
        """
        reply = request.reply()
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        local_zone = self.zone
        for name, rtype, rr in local_zone:
            # Check if label & type match
            if getattr(qname,self.eq)(name) and (qtype == rtype or
                                                 qtype == 'ANY' or
                                                 rtype == 'CNAME'):
                # If we have a glob match fix reply label
                if self.glob:
                    a = copy.copy(rr)
                    a.rname = qname
                    reply.add_answer(a)
                else:
                    reply.add_answer(rr)
                # Check for A/AAAA records associated with reply and
                # add in additional section
                if rtype in ['CNAME','NS','MX','PTR']:
                    for a_name,a_rtype,a_rr in local_zone:
                        if a_name == rr.rdata.label and a_rtype in ['A','AAAA']:
                            reply.add_ar(a_rr)
        if not reply.rr:
            reply.header.rcode = RCODE.SERVFAIL
        return reply


def server_start(zone=None, ttl=3600, **kwargs):
    if zone == None:
        def zone_builder():
            zone = StringIO.StringIO()
            server_zone_list(zone=zone)
            zone.seek(0)
            return zone
    elif zone == '-':
        def zone_builder():
            return sys.stdin
    else:
        def zone_builder():
            return open(zone)
    resolver = ZoneResolver(zone_builder, False, ttl)
    logger = DNSLogger("request,reply,truncated,error", False)
    def reload_dns_config(signum, frame):
        if signum == signal.SIGUSR1:
            resolver.load()
    signal.signal(signal.SIGUSR1, reload_dns_config)
    udp_server = DNSServer(resolver,
                           port=53,
                           address="",
                           logger=logger)
    udp_server.start()

def server_zone_list(zone=None, **kwargs):
    zone = zone or sys.stdout
    for profile in Profiles(**kwargs).list():
        profile.write_dns_file(zone)

def update_etc_hosts_file(hostip_tuples, output_file=None):
    """Update specified nodes in /etc/hosts
    Previous content is not lost

    :param hostip_tuples: generator of tuple (host, ip)
    :param output_file: destination file, default is /etc/hosts
    """
    BEGIN_MARKUP = '# CloudDNS prelude - DO NOT REMOVE\n'
    END_MARKUP = '# CloudDNS epilogue - DO NOT REMOVE\n'
    output_file = output_file or '/etc/hosts'
    if not osp.isfile(output_file):
        with open(output_file, 'a'):
            os.utime(output_file, None)
    with open(output_file, 'r+') as etc_hosts:
        lines  = etc_hosts.readlines()
        etc_hosts.seek(0)
        etc_hosts.truncate(0)
        previous_content_replaced = False
        between_markups = False
        for line in lines:
            if not between_markups:
                if line == BEGIN_MARKUP:
                    between_markups = True
                etc_hosts.write(line)
            else:
                if line == END_MARKUP:
                    previous_content_replaced = True
                    for hosts, ip in hostip_tuples:
                        etc_hosts.write("{} {}\n".format(ip.ljust(15, ' '), ' '.join(hosts)))
                    between_markups = False
                    etc_hosts.write(line)
        if not previous_content_replaced:
            etc_hosts.write(BEGIN_MARKUP)
            for hosts, ip in hostip_tuples:
                etc_hosts.write("{} {}\n".format(ip.ljust(15, ' '), ' '.join(hosts)))
            etc_hosts.write(END_MARKUP)

def etc_hosts_update(output_file=None, **kwargs):
    """Update /etc/hosts with all nodes available in configured projects

    :param output_file: destination file, default is /etc/hosts
    """
    update_etc_hosts_file(etc_hosts_generator(**kwargs), output_file)

def etc_hosts_generator(**kwargs):
    """Provides a generator of tuple (hosts, ip) for all nodes registered
    in the configured projects
    """
    generators = []
    for profile in Profiles(**kwargs).list():
        for project in profile.projects.values():
            generators.append(project.get_hostip_tuples())
    return itertools.chain(*generators)

def etc_hosts_list(**kwargs):
    """Print to standard output nodes available in all configured projects
    """
    for hosts, ip in etc_hosts_generator(**kwargs):
        print "{} {}".format(ip.ljust(15, ' '), ' '.join(hosts))


def cloud_dns(args=None):
    """cloud-dns entry point"""
    args = args or sys.argv[1:]
    from .version import version
    parser = argparse.ArgumentParser(
        description="DNS utilities on top of Apache libcloud"
    )
    parser.add_argument(
        '-V', '--version',
        action='version',
        version='%(proj)s ' + version
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        help='Verbose mode, -vv for more details, -vvv for 3rd-parties logs as well'
    )
    parser.add_argument(
        '-c', '--config-dir',
        help='Specify config root path [default: %(default)s]',
        dest='config_path',
        default=DEFAULT_CONFIG_PATH
    )
    subparsers = parser.add_subparsers(help='top commands')
    config_parser = subparsers.add_parser(
        'config',
        help='Manipulate DNS cloud configuration'
    )
    config_subparsers = config_parser.add_subparsers(help='config commands')
    config_push_parser = config_subparsers.add_parser(
        'push',
        help='Push configuration to Google Storage'
    )
    config_push_parser.add_argument('profile')
    config_push_parser.add_argument('bucket')
    config_push_parser.set_defaults(func=config_push)

    config_pull_parser = config_subparsers.add_parser(
        'pull',
        help='Retrieve latest configuration from Google Storage'
    )
    config_pull_parser.add_argument('profile')
    config_pull_parser.add_argument('bucket')
    config_pull_parser.add_argument(
        "identity",
        help='Keybase signature to use to decrypt configuration, for instance: github://tristan0x'
    )

    etc_hosts_parser = subparsers.add_parser(
        'etc-hosts',
        help='Manipulate DNS cloud configuration'
    )
    etc_hosts_subparsers = etc_hosts_parser.add_subparsers(help='etc-hosts commands')
    etc_hosts_update_parser = etc_hosts_subparsers.add_parser(
        "update",
        help='Required super-user privileges'
    )
    etc_hosts_update_parser.add_argument(
        '-o', '--ouput',
        dest='output_file',
        default='/etc/hosts',
        help='Output file [default: %(default)s]'
    )
    etc_hosts_update_parser.set_defaults(func=etc_hosts_update)
    etc_hosts_list_parser = etc_hosts_subparsers.add_parser(
        "list",
        help="List nodes in /etc/hosts format"
    )
    etc_hosts_list_parser.set_defaults(func=etc_hosts_list)

    dns_server_parser = subparsers.add_parser(
        'server',
        help='Start DNS server'
    )
    dns_server_subparsers = dns_server_parser.add_subparsers(help='server commands')
    dns_server_zone_parser = dns_server_subparsers.add_parser(
        "zone",
        help='Show DNS zone file'
    )
    dns_server_zone_parser.set_defaults(func=server_zone_list)
    dns_server_start_parser = dns_server_subparsers.add_parser(
        "start",
        help='Start DNS server'
    )
    dns_server_start_parser.add_argument(
        '--zone',
        default=None,
        help='Optional DNS zone file ("-" for stdin)'
    )
    dns_server_start_parser.add_argument(
        '--ttl',
        default=3600,
        type=int,
        help='Profile reload interval (in seconds) [default: %(default)s]'
    )
    dns_server_start_parser.set_defaults(func=server_start)

    config_pull_parser.set_defaults(func=config_pull)
    args = parser.parse_args(args)
    log_level = logging.WARN
    third_parties_log_level = logging.WARN
    if args.verbose:
        if args.verbose > 1:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
        if args.verbose >= 3:
            third_parties_log_level = logging.INFO
    logging.basicConfig(level=log_level)
    for logger in [
        'boto',
        'gnupg',
        'oauth2client',
        'oauth2_client',
        'requests',
    ]:
        logging.getLogger(logger).setLevel(third_parties_log_level)

    args.func(**vars(args))
