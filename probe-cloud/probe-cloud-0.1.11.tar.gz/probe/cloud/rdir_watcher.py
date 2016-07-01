import paramiko
import logging
import logging.config
import time
import re

logger = logging.getLogger(__name__)

class RDirWatcher(object):

    def __init__(self, cfg):
        logger.debug('cfg: %s', repr(cfg))
        self.key = paramiko.RSAKey.from_private_key_file(cfg['pkey_file'])
        self.hostnames = cfg['hostnames']
        self.port = 22
        self.username = cfg['username']
        self.watch_dir = cfg['watch_dir']
        self.watch_pattern = cfg['watch_pattern']
        self.watch_pattern_compile = re.compile(self.watch_pattern)
        self.watch_max_age = cfg['watch_max_age']
        logger.info('going to establish connections')
        self.connections = self.establish_connections()
        logger.info('self.connections: %s', self.connections)

    def close_connections(self):
        for host, conn in self.connections.iteritems():
            try:
                conn.close()
            except Exception as e:
                logger.exception('exception {} caught during closing ssh conn to host {}'.format(e, host))

        self.connections = None

    def establish_connections(self):

        connections = dict()
        for host in self.hostnames:
            logger.info('creating connection for host {}'.format(host))
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.load_system_host_keys()
                ssh.connect(host, self.port, pkey=self.key)
                connections[host] = ssh
            except Exception as e:
                logger.exception('exception during establishing connection to host {}'.format(host))

        return connections

    def check_connections(self):

        for host in self.connections:
            logger.debug('checking host: %s', host)
            ssh = self.connections[host]
            is_active = ssh.get_transport().is_active()
            logger.debug('is_active: %s', is_active)
            if is_active:
                try:
                    transport = ssh.get_transport()
                    transport.send_ignore()
                    logger.debug('send_ignore was successfull, conn is ok')
                except EOFError as e:
                    logger.exception('send_ignore was not successfull, conn is broken')
                    return False
            else:
                return False

        return True

    def reestablish_connections(self):
        logger.info('closing connections')
        self.close_connections()
        logger.info('establishing connections')
        self.connections = self.establish_connections()

    @staticmethod
    def check_stderr(cmd, stderr):
        stderr = stderr.readlines()
        logger.debug('cmd: {}, stderr: {}'.format(cmd, stderr))
        if stderr != []:
            raise CmdError(cmd, stderr)

    def check(self):

        if not self.check_connections():
            logger.warning('connections check was False')
            self.reestablish_connections()

        comps = set()
        for hostname in self.hostnames:
            try:
                logger.info('checking hostname %s', hostname)

                ssh = self.connections.get(hostname)
                if ssh is None:
                    logger.debug('ssh connection for host {} is None'.format(hostname))
                    continue

                cmd = 'ls {}'.format(self.watch_dir)
                _, stdout, stderr = ssh.exec_command(cmd)
                self.check_stderr(cmd, stderr)

                for line in stdout:
                    filename = line.strip()
                    # logger.debug('filename: {}'.format(filename.encode('utf-8')))

                    if self.watch_pattern_compile.match(filename):
                        logger.info('file match: {}'.format(filename))

                        delta_secs = self.get_last_modification_of_file(filename, ssh)
                        if delta_secs < self.watch_max_age:
                            comps_in_file = self.get_comps_in_file(filename, ssh)
                            logger.info('comps_in_file: %s', comps_in_file)
                            comps = comps.union(set(comps_in_file))

            except Exception as e:
                logger.error('Exception while checking hostname %s: %s', hostname, e)

        return comps

    def get_comps_in_file(self, filename, ssh):
        cmd = 'cat {}/{}'.format(self.watch_dir, filename)
        logger.debug('cmd_cat: {}'.format(cmd))
        _, stdout, stderr = ssh.exec_command(cmd)
        self.check_stderr(cmd, stderr)

        comps = list()
        for line_cat in stdout:
            comp = line_cat.strip()
            logger.debug('computer: {}'.format(comp))
            comps.append(comp)

        return comps

    def get_last_modification_of_file(self, filename, ssh):
        # %Y returns time of last modification of the file as seconds
        # since epoch
        cmd = 'stat --format "%Y" {}/{}'.format(self.watch_dir, filename)
        logger.debug('cmd_stat: {}'.format(cmd))
        _, stdout, stderr = ssh.exec_command(cmd)
        self.check_stderr(cmd, stderr)

        line_stat = stdout.readline()
        logger.debug('line_stat: {}'.format(line_stat))

        last_modification_secs = float(line_stat.strip())
        logger.debug('last_modification_secs: {}'.format(last_modification_secs))

        now_secs = time.time()
        logger.debug('now_secs: {}'.format(now_secs))

        delta_secs = now_secs - last_modification_secs
        logger.info('seconds since last modification: {}'.format(delta_secs))

        return delta_secs


class CmdError(Exception):

    def __init__(self, cmd, stderr):
        Exception.__init__(self)
        self.cmd = cmd
        self.stderr = stderr

    def __str__(self):
        'CmdError: Cmd: {}, stderr: {}'.format(self.cmd, self.stderr)
