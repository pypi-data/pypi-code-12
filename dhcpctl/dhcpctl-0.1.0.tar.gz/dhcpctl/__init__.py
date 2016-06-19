from isc_dhcp_leases import Lease, IscDhcpLeases
from arghandler import ArgumentHandler, subcmd
from tabulate import tabulate
from dhcpctl.distro import get_path_for_leases


@subcmd
def list(parser, context, args):
    parser.add_argument('--all', '-a', help='Also list inactive leases', action='store_true')
    args = parser.parse_args(args)

    lease_file = get_path_for_leases()
    rows = []
    if args.all:
        leases = IscDhcpLeases(lease_file).get()
    else:
        leases = IscDhcpLeases(lease_file).get_current()
    for lease in leases:
        rows.append([
            lease.ip,
            lease.hostname,
            lease.ethernet,
            lease.binding_state
        ])
    print(tabulate(rows, headers=['IP', 'Hostname', 'MAC', 'Binding state']))


def main():
    handler = ArgumentHandler(description='DHCPD Control tool')
    handler.run()


if __name__ == '__main__':
    main()
