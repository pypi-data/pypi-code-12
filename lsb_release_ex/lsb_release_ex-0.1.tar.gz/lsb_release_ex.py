"""
LSB release detection module for Debian/Ubuntu and Red Hat.

Ehanced Linux Standard Base version reporting module for Debian/Ubuntu and
Red Hat series. It is inspired by Debian implementaion in lsb-release.
"""

__author__ = "Like Ma"
__version__ = "0.1"
__license__ = "GPLv2"
__email__ = "likemartinma@gmail.com"


import sys
import os
import re
import platform
from subprocess import Popen, PIPE

# XXX: Update as needed
# This should really be included in apt-cache policy output... it is already
# in the Release file...
RELEASE_CODENAME_LOOKUP = {
    '1.1': 'buzz',
    '1.2': 'rex',
    '1.3': 'bo',
    '2.0': 'hamm',
    '2.1': 'slink',
    '2.2': 'potato',
    '3.0': 'woody',
    '3.1': 'sarge',
    '4.0': 'etch',
    '5.0': 'lenny',
}

TESTING_CODENAME = 'unknown.new.testing'

# e.g.
#  CentOS release 5.9 (Final)
#  Red Hat Enterprise Linux Server release 5.4 (Tikanga)
#  Enterprise Linux Enterprise Linux Server release 5.5 (Carthage)
REDHAT_RELEASE_RE = re.compile(r'^(.*)\s+release\s+([\w\.]+)\s*\(([^\)]+)\)')


def lookup_codename(release, unknown=None):
    m = re.match(r'(\d+)\.(\d+)(r(\d+))?', release)
    if not m:
        return unknown

    shortrelease = '%s.%s' % m.group(1, 2)
    return RELEASE_CODENAME_LOOKUP.get(shortrelease, unknown)

# LSB compliance packages... may grow eventually
PACKAGES = ('lsb-core lsb-cxx lsb-graphics lsb-desktop lsb-qt4 '
            'lsb-languages lsb-multimedia lsb-printing')

modnamere = re.compile(r'lsb-(?P<module>[a-z0-9]+)-'
                       r'(?P<arch>[^ ]+)(?: \(= (?P<version>[0-9.]+)\))?')


# If a module is ever released that only appears in >= version, deal
# with that here
LSB_VERSIONS_TABLE = {
    '3.0': (None, ['2.0', '3.0']),

    '3.1': (
        {
            'desktop': ['3.1'],
            'qt4': ['3.1']
        },
        ['2.0', '3.0', '3.1']
    ),

    '3.2': (
        {
            'desktop': ['3.1', '3.2'],
            'qt4': ['3.1'],
            'printing': ['3.2'],
            'languages': ['3.2'],
            'multimedia': ['3.2'],
            'cxx': ['3.0', '3.1', '3.2'],
        },
        ['2.0', '3.0', '3.1', '3.2']
    ),

    '4.0': (
        {
            'desktop': ['3.1', '3.2', '4.0'],
            'qt4': ['3.1'],
            'printing': ['3.2', '4.0'],
            'languages': ['3.2', '4.0'],
            'multimedia': ['3.2', '4.0'],
            'security': ['4.0'],
            'cxx': ['3.0', '3.1', '3.2', '4.0']
        },
        ['2.0', '3.0', '3.1', '3.2', '4.0']
    ),
}


def valid_lsb_versions(version, module):
    if version not in LSB_VERSIONS_TABLE:
        return [version]

    table, default = LSB_VERSIONS_TABLE[version]
    return table.get(module, default)

try:
    set  # introduced in 2.4
except NameError:
    import sets
    set = sets.Set


# This is Debian-specific at present
def check_modules_installed():
    try:
        return tuple(os.listdir('/etc/lsb-release.d'))
    except:
        # Find which LSB modules are installed on this system
        proc = Popen(['dpkg-query', '-f', r'${Version} ${Provides}\n',
                      '-W'] + PACKAGES.split(),
                     stdout=PIPE, stderr=open('/dev/null', 'w'),
                     close_fds=True)

        modules = set()
        for i in proc.stdout:
            version, provides = i.strip().decode().split(' ', 1)
            version = version.split('-', 1)[0]
            for pkg in provides.split(','):
                mob = modnamere.search(pkg)
                if not mob:
                    continue

                mgroups = mob.groupdict()
                # If no versioned provides...
                if mgroups.get('version'):
                    module = '%(module)s-%(version)s-%(arch)s' % mgroups
                    modules.add(module)
                else:
                    module = mgroups['module']
                    for v in valid_lsb_versions(version, module):
                        mgroups['version'] = v
                        module = '%(module)s-%(version)s-%(arch)s' % mgroups
                        modules.add(module)

        modules = list(modules)
        modules.sort()
        proc.wait()
        return modules

longnames = {'v': 'version', 'o': 'origin', 'a': 'suite',
             'c': 'component', 'l': 'label'}


def parse_policy_line(data):
    retval = {}
    bits = data.split(',')
    for bit in bits:
        kv = bit.split('=', 1)
        if len(kv) > 1:
            k, v = kv[:2]
            if k in longnames:
                retval[longnames[k]] = v
    return retval


def parse_apt_policy():
    data = []

    proc = Popen(("apt-cache", "policy"),
                 stdout=PIPE, stderr=open('/dev/null', 'w'),
                 close_fds=True, env={"LANG": "C"})
    for i in proc.stdout:
        i = i.strip()
        m = re.match(r'(\d+)', i)
        if m:
            priority = int(m.group(1))

        if i.startswith('release'):
            bits = i.split(' ', 1)
            if len(bits) > 1:
                data.append((priority, parse_policy_line(bits[1])))

    proc.wait()
    return data


def guess_release_from_apt(origin='Debian', component='main',
                           ignoresuites=('experimental'),
                           label='Debian'):
    releases = parse_apt_policy()

    if not releases:
        return None

    # We only care about the specified origin, component, and label
    releases = [x for x in releases if (
        x[1].get('origin', '') == origin and
        x[1].get('component', '') == component and
        x[1].get('label', '') == label)]

    # Check again to make sure we didn't wipe out all of the releases
    if not releases:
        return None

    releases.sort()
    releases.reverse()

    # We've sorted the list by descending priority, so the first entry should
    # be the "main" release in use on the system

    return releases[0][1]


def debian_version_io(fp):
    release = fp.read().strip()

    if not release[0:1].isalpha():
        # /etc/debian_version should be numeric
        codename = lookup_codename(release, 'n/a')
        return {'RELEASE': release, 'CODENAME': codename}

    if release.endswith('/sid'):
        if release.rstrip('/sid').lower().isalpha() != 'testing':
            global TESTING_CODENAME
            TESTING_CODENAME = release.rstrip('/sid')

        return {'RELEASE': 'testing/unstable'}

    return {'RELEASE': release}


def guess_debian_release():
    distinfo = {'ID': 'Debian'}

    kern = os.uname()[0]
    if kern in ('Linux', 'Hurd', 'NetBSD'):
        distinfo['OS'] = 'GNU/'+kern
    elif kern == 'FreeBSD':
        distinfo['OS'] = 'GNU/k'+kern
    else:
        distinfo['OS'] = 'GNU'

    if os.path.exists('/etc/debian_version'):
        try:
            distinfo.update(debian_version_io(open('/etc/debian_version')))
        except IOError as msg:
            sys.stderr.write('Unable to open /etc/debian_version: %s\n' % msg)
            distinfo['RELEASE'] = 'unknown'

    # Only use apt information if we did not get the proper information
    # from /etc/debian_version or if we don't have a codename
    # (which will happen if /etc/debian_version does not contain a
    # number but some text like 'testing/unstable' or 'lenny/sid')
    #
    # This is slightly faster and less error prone in case the user
    # has an entry in his /etc/apt/sources.list but has not actually
    # upgraded the system.
    rinfo = guess_release_from_apt()
    if rinfo and not distinfo.get('CODENAME'):
        release = rinfo.get('version')
        if release:
            codename = lookup_codename(release, 'n/a')
        else:
            release = rinfo.get('suite', 'unstable')
            if release == 'testing':
                # Would be nice if I didn't have to hardcode this.
                codename = TESTING_CODENAME
            else:
                codename = 'sid'
        distinfo.update({'RELEASE': release, 'CODENAME': codename})

    distinfo['DESCRIPTION'] = ' '.join(
        filter(None, (distinfo.get('ID'), distinfo.get('OS'),
                      distinfo.get('RELEASE'), distinfo.get('CODENAME'))))

    return distinfo


def get_debian_lsb_information(fp):
    distinfo = {}

    try:
        for line in fp:
            line = line.strip()
            if not line:
                continue
            # Skip invalid lines
            if not '=' in line:
                continue
            var, arg = line.split('=', 1)
            if var.startswith('DISTRIB_'):
                var = var[8:]
                if arg.startswith('"') and arg.endswith('"'):
                    arg = arg[1:-1]
                if arg:  # Ignore empty arguments
                    distinfo[var] = arg
    except IOError as msg:
        sys.stderr.write('Unable to open /etc/lsb-release: %s\n' % msg)

    return distinfo


def get_redhat_lsb_information(fp):
    distinfo = {}

    try:
        m = REDHAT_RELEASE_RE.match(fp.readline())
        if m:
            distinfo["DESCRIPTION"] = m.group(0)
            id = m.group(1)

            if id == "Red Hat Enterprise Linux Server":
                distinfo["ID"] = "RedHatEnterpriseServer"
            elif id == "Enterprise Linux Enterprise Linux Server":
                distinfo["ID"] = "EnterpriseEnterpriseServer"
            else:
                distinfo["ID"] = id

            distinfo["RELEASE"] = m.group(2)
            distinfo["CODENAME"] = m.group(3)
    except IOError as msg:
        sys.stderr.write("Unable to open /etc/redhat-release: %s\n" % msg)

    return distinfo


# Whatever is guessed above can be overridden in /etc/lsb-release
def get_lsb_information():
    if os.path.exists("/etc/lsb-release"):
        distinfo = get_debian_lsb_information(open("/etc/lsb-release"))
    else:
        if os.path.exists("/etc/enterprise-release"):
            release = "/etc/enterprise-release"
        elif os.path.exists("/etc/redhat-release"):
            release = "/etc/redhat-release"
        else:
            release = None

        distinfo = get_redhat_lsb_information(open(release)) if release else {}

    if not distinfo:
        id_, release, codename = platform.linux_distribution()
        distinfo["ID"] = id_
        distinfo["RELEASE"] = release
        distinfo["CODENAME"] = codename
        distinfo["DESCRIPTION"] = "%s %s %s" % (id, release, codename)

    return distinfo


def get_distro_information():
    lsbinfo = get_lsb_information()
    # OS is only used inside guess_debian_release anyway
    for key in ('ID', 'RELEASE', 'CODENAME', 'DESCRIPTION'):
        if key not in lsbinfo:
            distinfo = guess_debian_release()
            distinfo.update(lsbinfo)
            return distinfo
    else:
        return lsbinfo


if __name__ == '__main__':
    distinfo = get_distro_information()
    verinfo = check_modules_installed()
    if verinfo:
        lsb_version = ":".join(verinfo)
    else:
        lsb_version = ''

    print('''LSB Version:    %s
Distributor ID: %s
Description:    %s
Release:        %s
Codename:       %s''' % (lsb_version,
                         distinfo.get("ID"),
                         distinfo.get("DESCRIPTION"),
                         distinfo.get("RELEASE"),
                         distinfo.get("CODENAME")))

# vim: ts=4 sw=4 sts=4 et:
