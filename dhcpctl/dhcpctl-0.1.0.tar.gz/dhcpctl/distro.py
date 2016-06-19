import distro


def get_path_for_leases():
    if distro.id() == 'debian' or 'debian' in distro.like():
        return '/var/lib/dhcp/dhcpd.leases'
    else:
        raise NotImplementedError('Distro not implemented')
