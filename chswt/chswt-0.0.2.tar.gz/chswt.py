#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import subprocess


def cl():
    parse = argparse.ArgumentParser(prog='chswt3.py')
    parse.add_argument(
        '--check-hosts', type=str, default='77.88.8.8,8.8.8.8',
        metavar='host[,host]', help='Remote hosts for checking channel '
                                    '(default: 77.88.8.8, 8.8.8.8)')
    parse.add_argument(
        '--test', help='Test channel', metavar='eth2[,eth0]', type=str)
    parse.add_argument(
        '--scripts-dir', type=str, metavar='path', default='/etc/chswt',
        help='Directory where stored scripts (default: /etc/chswt)')
    parse.add_argument(
        '--manual', type=str, metavar='eth2',
        help='Manual set options of interface')
    parse.add_argument(
        '--version', action='version', version='%(prog)s v0.0.1')
    parse.add_argument(
        '--monitor', type=str, metavar='eth2,eth0',
        help='Check channel and execute third-party script (is iface name),'
             ' desc priority')
    parse.add_argument(
        '--restart', type=str, metavar='openvpn[,ssh]',
        help='Services which must be restarted when change channel')

    args_keys = parse.parse_args()
    return parse, args_keys


class ChannelCheck:
    def __init__(self, **kwargs):
        self.check_hosts = kwargs.get('check_hosts')
        self.interfaces = kwargs.get('interfaces')

    def ping(self, interface):
        if isinstance(self.check_hosts, str):
            self.check_hosts = self.check_hosts.split(',')

        for host in self.check_hosts:
            command = 'ping -I {iface} -c 5 {host}'.format(
                iface=interface.strip(), host=host.strip())

            sp = subprocess.call(
                command.split(), stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)

            if sp == 0:
                return True
        return False

    def look_for(self):
        """ Look for working channel """
        if isinstance(self.interfaces, str):
            self.interfaces = self.interfaces.split(',')

        for interface in self.interfaces:
            if self.ping(interface):
                return interface.strip()
        return False

    @staticmethod
    def get_cur_interface():
        """
        Getting default interface.
        :return: string
        """

        c1 = subprocess.Popen(['/sbin/route', '-n'], stdout=subprocess.PIPE)
        c2 = subprocess.Popen(
            ['head', '-n', '3'], stdin=c1.stdout, stdout=subprocess.PIPE)
        c3 = subprocess.Popen(
            ['awk', '$1 == "0.0.0.0" {print $8}'], stdin=c2.stdout,
            stdout=subprocess.PIPE)

        c1.stdout.close()
        c2.stdout.close()
        result = c3.communicate()[0].strip().decode('utf-8')
        c3.stdout.close()

        return result


class ThirdParty:
    def __init__(self, **kwargs):
        self.restart_list = kwargs.get('restart')
        self.scripts_dir = kwargs.get('scripts_dir')

    def restart(self):
        """ Tested in Ubuntu """
        if not self.restart_list:
            return {}

        if isinstance(self.restart_list, str):
            self.restart_list = self.restart_list.split(',')

        result = {}

        for service in self.restart_list:
            print('Restart service: {}'.format(service))
            command = '/usr/sbin/service {service} restart'.format(
                service=service.strip())
            sp = subprocess.call(
                command.split(), stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)

            if sp == 0:
                result[service] = True
        return result

    def execute_script(self, script):
        path_to_script = os.path.join(self.scripts_dir, script)
        if not os.path.exists(path_to_script):
            print('Error: script {} not found'.format(path_to_script))
            return False

        print('Execute script: {}'.format(path_to_script))
        sp = subprocess.call(
            path_to_script.split(), stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        if sp == 0:
            return True
        return False


def main():
    h, args = cl()

    if args.monitor:
        check = ChannelCheck(**{
            'check_hosts': args.check_hosts, 'interfaces': args.monitor})

        main_channel = args.monitor.split(',')[0]
        if check.ping(main_channel):
            print('Main channel ({}) is available'.format(main_channel))
            if check.get_cur_interface() == main_channel:
                print('And main channel is current channel. Exit.')
                return True
            else:
                print('Switch to main channel...')
                work_channel = main_channel
        else:
            print('Main channel ({}) isn\'t available, look for working '
                  'channel...'.format(main_channel))
            work_channel = check.look_for()

        if not work_channel:
            print('Working channel not found. Exit.')
            return False

        print('{} is work channel'.format(work_channel))
        tp = ThirdParty(**{
            'restart': args.restart, 'scripts_dir': args.scripts_dir})
        tp.execute_script(work_channel)
        tp.restart()
        return True

    if args.test:
        check = ChannelCheck(**{
            'check_hosts': args.check_hosts, 'interfaces': args.test})
        for interface in args.test.split(','):
            if check.ping(interface):
                print('{} is available'.format(interface))
            else:
                print('{} isn\'t available'.format(interface))
        return True

    if args.manual:
        tp = ThirdParty(**{
            'restart': args.restart, 'scripts_dir': args.scripts_dir})
        if tp.execute_script(args.manual.strip()):
            tp.restart()
        else:
            print('Problem')
            return False

        return True

    h.print_help()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
