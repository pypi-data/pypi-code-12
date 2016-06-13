# -*- coding: utf-8 -*-

import re
import shutil
import subprocess


class Supervisor:
    def __init__(self):
        self.supervisorctl = shutil.which('supervisorctl')
        self.supervisord_conf = '/etc/supervisor/supervisord.conf'

    def build_bin(self):
        return '{} -c {}'.format(self.supervisorctl, self.supervisord_conf)

    @staticmethod
    def clean_result(r):
        return r.decode().strip()

    def status(self, process=''):
        r = self.clean_result(subprocess.check_output(
            '{} status {}'.format(self.build_bin(), process), shell=True))

        if process:
            return self.status_parser(r)
        else:
            return [self.status_parser(item) for item in r.split('\n')]

    def add(self, process):
        r = self.clean_result(subprocess.check_output(
            '{} add {}'.format(self.build_bin(), process), shell=True))

        return self.add_parser(r)

    def reread(self):
        r = self.clean_result(subprocess.check_output(
            '{} reread'.format(self.build_bin()), shell=True))

        return [self.reread_parser(item) for item in r.split('\n')]

    def stop(self, process):
        r = self.clean_result(subprocess.check_output(
            '{} stop {}'.format(self.build_bin(), process), shell=True))

        return self.stop_parser(r)

    def restart(self, process):
        r = self.clean_result(subprocess.check_output(
            '{} restart {}'.format(self.build_bin(), process), shell=True))

        return self.restart_parser(r)

    def start(self, process):
        r = self.clean_result(subprocess.check_output(
            '{} start {}'.format(self.build_bin(), process), shell=True))

        return self.start_parser(r)

    def remove(self, process):
        r = self.clean_result(subprocess.check_output(
            '{} remove {}'.format(self.build_bin(), process), shell=True))

        return self.remove_parser(r)

    @staticmethod
    def status_parser(result):
        patterns = [
            # infinity1                      RUNNING   pid 10136, uptime 0:00:06
            ['RUNNING', '(?P<name>\w+)\s+(?P<status>[RUNIG]+)\s+\w+\s+'
                        '(?P<pid>\d+),\s+\w+\s+(?P<uptime>[0-9:]+)$'],
            # infinity1                        STOPPED   Jun 12 07:16 PM
            ['STOPPED', '(?P<name>\w+)\s+(?P<status>[STOPED]+)\s+'
                        '(?P<stopped>\w+\s\d[0-9:PMAM ]+)$'],
            # infinity2: ERROR (no such process)
            ['ERROR', '(?P<name>\w+):\s+(?P<status>[ERO]+)\s\('
                      '(?P<msg>[no suchprce]+)\)$'],
            # infinity1  FATAL  Exited too quickly (process log may have
            #  details)
            # and
            # infinity1  BACKOFF  Exited too quickly (process log may have
            #  details)
            ['FATAL', '(?P<name>\w+)\s+(?P<status>[FATLBCKO]+)\s+'
                      '(?P<msg>[Exited oquckly(prsgmahv)]+)$']]

        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] == 'RUNNING':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'pid': m.group('pid'),
                        'uptime': m.group('uptime')}
                elif item[0] == 'STOPPED':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'stopped': m.group('stopped')}
                elif item[0] in ['ERROR', 'FATAL']:
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'msg': m.group('msg')}
        return {}

    @staticmethod
    def reread_parser(result):
        patterns = [
            # No config updates to processes
            ['EMPTY', '(?P<msg>[No cnfigupdatesr]+)$'],
            # infinity1: available
            ['AVAILABLE', '(?P<name>\w+):\s(?P<status>[avilbe]+)$']]

        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] == 'EMPTY':
                    return {
                        'msg': m.group('msg')}
                elif item[0] == 'AVAILABLE':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status')}
        return {}

    @staticmethod
    def add_parser(result):
        patterns = [
            # infinity1: added process group
            ['SUCCESS', '(?P<name>\w+):\s(?P<msg>[adeprocsgup ]+)$'],
            # ERROR: process group already active
            ['ERROR1', '(?P<status>[ERO]+):\s(?P<msg>[procesgualdytiv ]+)$'],
            # ERROR: no such process/group: infinity12
            ['ERROR2', '(?P<status>[ERO]+):\s(?P<msg>[nosuchproes/gu ]+):\s'
                       '(?P<name>\w+)$']]

        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] == 'SUCCESS':
                    return {
                        'name': m.group('name'),
                        'msg': m.group('msg'),
                        'result': True}
                elif item[0] == 'ERROR1':
                    return {
                        'status': m.group('status'),
                        'msg': m.group('msg'),
                        'result': False}
                elif item[0] == 'ERROR2':
                    return {
                        'status': m.group('status'),
                        'msg': m.group('msg'),
                        'result': False}
        return {}

    @staticmethod
    def stop_parser(result):
        patterns = [
            # infinity1: stopped
            ['SUCCESS', '(?P<name>\w+):\s(?P<status>[stoped]+)$'],
            # infinity1: ERROR (not running)
            ['ERROR1', '(?P<name>\w+):\s(?P<status>[ERO]+)\s\('
                       '(?P<msg>[notruig ]+)\)$'],
            # infinity12: ERROR (no such process)
            ['ERROR2', '(?P<name>\w+):\s(?P<status>[ERO]+)\s\('
                       '(?P<msg>[nosuchpres ]+)\)$']
        ]

        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] == 'SUCCESS':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'result': True}
                elif item[0] == 'ERROR1':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'result': False,
                        'msg': m.group('msg')}
                elif item[0] == 'ERROR2':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'result': False,
                        'msg': m.group('msg')}
        return {}

    @staticmethod
    def restart_parser(result):
        patterns = [
            # infinity1: stopped
            # infinity1: started
            ['SUCCESS1', '(?P<name_stop>\w+):\s(?P<status_stop>[stoped]+)\s'
                         '(?P<name_start>\w+):\s(?P<status_start>[stared]+)$'],
            # infinity1: ERROR (not running)
            # infinity1: started
            ['SUCCESS2', '(?P<name_stop>\w+):\s(?P<status_stop>[ERO]+)\s\('
                         '(?P<msg_stop>[notruig ]+)\)\s(?P<name_start>\w+):\s'
                         '(?P<status_start>[stared]+)$'],
            # infinity12: ERROR (no such process)
            # infinity12: ERROR (no such process)
            ['ERROR1', '(?P<name_stop>\w+):\s(?P<status_stop>[ERO]+)\s\('
                       '(?P<msg_stop>[nosuchpres ]+)\)\s(?P<name_start>\w+):\s'
                       '(?P<status_start>\w+)\s\('
                       '(?P<msg_start>[nosuchpres ]+)\)$']]

        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] in ['SUCCESS1', 'SUCCESS2']:
                    try:
                        return {
                            'name': m.group('name_start'),
                            'status': m.group('status_start'),
                            'msg_stop': m.group('msg_stop'),
                            'result': True}
                    except IndexError:
                        return {
                            'name': m.group('name_start'),
                            'status': m.group('status_start'),
                            'result': True}
                if item[0] == 'ERROR1':
                    return {
                        'name': m.group('name_start'),
                        'status': m.group('status_start'),
                        'msg_start': m.group('msg_start'),
                        'result': False}
        return {}

    @staticmethod
    def start_parser(result):
        patterns = [
            # infinity2: started
            ['SUCCESS', '(?P<name>\w+):\s(?P<status>[stared]+)$'],
            # infinity2: ERROR (already started)
            ['ERROR1', '(?P<name>\w+):\s(?P<status>[ERO]+)\s\('
                       '(?P<msg>[alredyst ]+)\)$'],
            # infinity1: ERROR (spawn error)
            ['ERROR2', '(?P<name>\w+):\s(?P<status>[ERO]+)\s\('
                       '(?P<msg>[spawnero ]+)\)$'],
            # infinity12: ERROR (no such process)
            ['ERROR3', '(?P<name>\w+):\s(?P<status>[ERO]+)\s\('
                       '(?P<msg>[nosuchprces ]+)\)$'],
        ]
        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] == 'SUCCESS':
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'result': True}
                if item[0] in ['ERROR1', 'ERROR2', 'ERROR3']:
                    return {
                        'name': m.group('name'),
                        'status': m.group('status'),
                        'msg': m.group('msg'),
                        'result': False}
        return {}

    @staticmethod
    def remove_parser(result):
        patterns = [
            # infinity1: removed process group
            ['SUCCESS', '(?P<name>\w+):\s(?P<msg>[removdpcsgu ]+)$'],
            # ERROR: process/group still running: infinity2
            ['ERROR1', '(?P<status>\w+):\s(?P<msg>[proces/gustiln ]+):\s'
                       '(?P<name>\w+)$'],
            # ERROR: no such process/group: infinity12
            ['ERROR2', '(?P<status>\w+):\s(?P<msg>[nosuchpres/gu ]+):\s'
                       '(?P<name>\w+)$']]

        for item in patterns:
            m = re.match(item[1], result)
            if m:
                if item[0] == 'SUCCESS':
                    return {
                        'name': m.group('name'),
                        'msg': m.group('msg'),
                        'result': True}
                elif item[0] in ['ERROR1', 'ERROR2']:
                    return {
                        'name': m.group('name'),
                        'msg': m.group('msg'),
                        'status': m.group('status'),
                        'result': False}
        return {}
