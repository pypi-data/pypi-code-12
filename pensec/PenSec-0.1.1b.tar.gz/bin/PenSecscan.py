#!/usr/bin/python


import argparse
from PenSecrecon import PScon
from psxgrab import PSXgrab
import psxgrab
from inspect import isclass


def main(url, recon, proxy):
    """
    Main method, start scan, and exploit retrieving
    """
    PenSecrecon = PScon(proxy)
    PenSecrecon_results = PenSecrecon.scan(url)

    print_recon(PenSecrecon_results)
    if not recon:
        # Search sploits
        grabbers_objects = []
        for grabber in get_grabbers():
            grabbers_objects.append(grabber())
        print_plugins_sploits(grabbers_objects, PenSecrecon_results)
        print_theme_sploits(grabbers_objects, PenSecrecon_results)
        print_version_sploits(grabbers_objects, PenSecrecon_results)


def print_recon(PenSecrecon_results):
    # Recon
    for name, result in PenSecrecon_results['printable_results'].items():
        if result is not None:
            print "[*] %s" % name
            if isinstance(result, list):
                for result_line in result:
                    print "  [+] %s" % result_line
            else:
                print "  [+] %s" % result


def print_plugins_sploits(grabbers, PenSecrecon_results):
    # Search for vulnerable plugins
    print "[*] Modules"
    for plugin in PenSecrecon_results['plugins']:
        print "  [+] %s" % plugin
        for grabber in grabbers:
            sploits = grabber.search(plugin, 'plugin')
            for sploit in sploits:
                print "    [!] %s" % sploit


def print_theme_sploits(grabbers, PenSecrecon_results):
    # Search theme related sploits
    theme = PenSecrecon_results['printable_results']['Theme']
    if theme is not None:
        print "[*] Searching sploits for theme %s" % theme
        for grabber in grabbers:
            sploits = grabber.search(theme, 'theme')
            for sploit in sploits:
                print "  [+] %s" % sploit


def print_version_sploits(grabbers, PenSecrecon_results):
    # Search wordpress version related sploits
    version = PenSecrecon_results['printable_results']['Version']
    if version is not None:
        print "[*] Searching sploits for wordpress %s" % version
        for grabber in grabbers:
            sploits = grabber.search(version, 'version')
            for sploit in sploits:
                print "  [+] %s" % sploit


def get_grabbers():
    """
    Get all exploit grabber classes
    """
    grabbers = []
    for classname in dir(psxgrab):
        try:
            custom_class = getattr(psxgrab, classname)
            if isclass(custom_class):
                if issubclass(custom_class, PSXgrab):
                    if custom_class.__name__ != PSXgrab.__name__:
                        grabbers.append(custom_class)
        except TypeError:
            pass
    return grabbers


if __name__ == "__main__":
    """
    Entrypoint
    """
    print """
   -----------------------------------------
   | Pentest Wordpress                     |
   | PenSec                                |
   -----------------------------------------
    """
    parser = argparse.ArgumentParser(description='Xploit Wordpress')
    parser.add_argument('-u', '--url',
                        action='store',
                        dest='url',
                        required=True,
                        help='victim url')
    parser.add_argument('-r', '--recon',
                        action='store_true',
                        dest='recon_only',
                        default=False,
                        help='Just recon')
    parser.add_argument('-t', '--tor',
                        action='store_true',
                        dest='tor',
                        default=False,
                        help='Use Tor')
    parser.add_argument('-p', '--proxy',
                        action='store',
                        dest='proxy',
                        default=None,
                        help='Use proxy')
    args = parser.parse_args()

    # Configure proxy
    proxy = None
    if args.tor:
        proxy = {"http": "127.0.0.1:9050",
                 "https": "127.0.0.1:9050"}

    if args.proxy is not None:
        proxy = {"http": args.proxy,
                 "https": args.proxy}

    main(args.url, args.recon_only, proxy)
