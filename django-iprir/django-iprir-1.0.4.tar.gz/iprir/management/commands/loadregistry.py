"""
loadregistry.py 12/2014

custom django-admin command for importing allocated blocks
"""


import urllib.parse
import urllib.request

from ftplib import FTP

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from iprir.models import Registry, TLD, InetNum
from iprir.utils import ip2int


def get_toplevel_domains():

    """
    Retrieve countrycodes and create Top Level Domain records with desciption
    """

    stream = urllib.request.urlopen(
        'https://raw.github.com/pudo/lobbytransparency/master/etl/countrycodes.csv'
    )
    csvdata = str(stream.read(), 'utf-8')

    # Loop twice to make sure  countries are linked properly
    for csvline in csvdata.split('\r\n'):

        if csvline and csvline[0] == '"':
            csvline = csvline[csvline.rindex('"')+1:]

        try:
            (_, _, _, tmp_iso3, tmp_iso2, _, tmp_isonum, tmp_country, _) = csvline.split(',', 8)

            if len(tmp_iso2) == 2 and len(tmp_iso3) == 3 and tmp_isonum.isdigit():

                tmp_iso2 = tmp_iso2.lower()
                tmp_country = tmp_country.title()

                try:
                    tld = TLD.objects.get(domain=tmp_iso2)

                except TLD.DoesNotExist:
                    tld = TLD(domain=tmp_iso2, type='country-code')

                finally:
                    tld.description = tmp_country
                    tld.save()

        except ValueError:
            pass


def get_ipblocks():

    """
    Retrieve latest IP block files from RIPE
    """

    registries = ['afrinic', 'apnic', 'arin', 'lacnic', 'ripencc']

    blocks = [
        'iana||ipv4|10.0.0.0|16777216|19700401|reserved',
        'iana||ipv4|127.0.0.0|16777216|19700401|reserved',
        'iana||ipv4|172.16.0.0|1048576|19700401|reserved',
        'iana||ipv4|224.0.0.0|268435456|19700401|multicast',
    ]

    ftp = FTP('ftp.ripe.net')
    ftp.login()

    for region in registries:
        extended_tag = "-extended"
        remote_dir = '/pub/stats/' + region
        md5_filename = 'delegated-' + region + '-latest.md5'

        ftp.cwd(remote_dir)

        directory_list = []
        ftp.retrlines('LIST', callback=directory_list.append)
        for check_filename in directory_list:
            if md5_filename in check_filename:
                extended_tag = ""

        get_filename = md5_filename.replace(region, region + extended_tag)[:-4]

        try:
            ftp.retrlines("RETR %s" % get_filename, callback=blocks.append)

        except:
            pass

    ftp.quit()

    return blocks


def build_inetnum():

    """
    Create inetnum records
    """

    teller = 0
    ip_blocks = get_ipblocks()

    for ip_line in ip_blocks:

        try:
            (
                tmp_registry, tmp_country, tmp_protocol, tmp_ipstart, tmp_iprange, _, tmp_status
            ) = ip_line.split('|', 6)

            if tmp_protocol == 'ipv4':

                tmp_country = tmp_country.lower()
                ipnumstart = ip2int(tmp_ipstart)
                ipnumends = ipnumstart + int(tmp_iprange) - 1

                try:
                    registry = Registry.objects.get(registryDesc=tmp_registry)

                except Registry.DoesNotExist:
                    registry = Registry.objects.create(registryDesc=tmp_registry)

                try:
                    tld = TLD.objects.get(domain=tmp_country)

                except TLD.DoesNotExist:
                    tld = TLD.objects.create(domain=tmp_country, description=tmp_registry, type='generic')

                try:
                    inetnum = InetNum.objects.get(inetNumFrom=ipnumstart)

                except InetNum.DoesNotExist:
                    inetnum = InetNum(inetNumFrom=int(ipnumstart))

                teller += 1

                inetnum.inetNumTo = int(ipnumends)
                inetnum.tld_id = tld.pk
                inetnum.registry_id = registry.pk
                inetnum.inetNumValid = True if tld.pk or tmp_registry == 'iana' else False
                inetnum.inetNumAllocated = True if "allocated" in tmp_status else False

                if tld.pk and registry.pk:
                    if tld.registry_id != registry.pk:
                        tld.registry_id = registry.pk
                        tld.save()

                inetnum.save()
                teller += 1

        except ValueError:
            pass


    print(teller, 'inetnums touched')

    return teller


def clean_inetnum():

    """
    Delete old inetnum records
    """

    teller = 0

    # Delete untouched records
    time_threshold = timezone.now() - timedelta(hours=3)
    inetnums = InetNum.objects.filter(lastModified__lt=time_threshold)

    for inetnum in inetnums:
        inetnum.delete()
        teller += 1

    print(teller, 'inetnums deleted')

    return teller


class Command(BaseCommand):

    """
    Main loop
    """

    def handle(self, *args, **options):

        try:
            if not TLD.objects.first():
                get_toplevel_domains()

            if build_inetnum():
                clean_inetnum()

        except IOError as err:
            print('Error=' + str(err))
