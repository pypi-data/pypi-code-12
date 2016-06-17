"""
This module contains utils for the suprabackup_receive tool

"""
import sys
import os
import datetime

from ..models import Host


class SupraReceive:
    """
    A simple object to handle config, db, logger and utils for
    suprabackup_receive

    """
    FILE_FMT = '{}-{}.tar.gz'


    def __init__(self, config, logger, session):
        """
        Sets up SupraReceive with given config/logger and db connection

        """
        self.config = config
        self.logger = logger
        self.session = session


    def receive(self, ip):
        """
        Receives a backup and updates the database
        This is the main method of SupraReceive

        """
        self.logger.info("Receiving backup from {}".format(ip))
        host = self.get_host(ip)
        start = datetime.datetime.now()
        path = self.build_backup_path(self.create_host_backup_dir(host), start)
        job = host.new_job(start, path)
        self.session.add(job)
        self.session.commit()
        self.logger.debug("Starting upload for host {} (Job id {})".format(host.name, job.id))
        self.pipe_upload(path)
        self.logger.debug("Upload ended for host {} (Job id {})".format(host.name, job.id))
        job.end()
        self.logger.info("Backup received for host {} (Job id {})".format(host.name, job.id))


    def get_host(self, ip):
        """
        Retrieves an Host ORM mapping from an IP address

        """
        try:
            return self.session.query(Host).filter(Host.ip==ip).one()
        except Exception as e:
            self.logger.critical("Cannot find client hostname for IP {}: {}"
                                 .format(ip, e))
            sys.exit(1)


    def build_backup_path(self, host_path, start):
        """
        Returns the full path of the backup will be stored

        """
        import os

        prefix = self.config['file_prefix']
        f = self.FILE_FMT.format(prefix, start.strftime("%Y-%m-%d_%H-%M"))
        return os.path.join(host_path, f)


    def create_host_backup_dir(self, host):
        """
        Creates the host backup dir and return it

        """
        path = os.path.join(self.config['base_path'], host.name)
        try:
            if not os.path.isdir(path):
                self.logger.info("Creating directory {0}".format(path))
                os.mkdir(path, 0755)
            else:
                self.logger.debug("Directory {0} already exists, skipping"
                                  .format(path))
            return path
        except OSError as e:
            self.logger.critical("Cannot make directory {0}: [{1}] {2}"
                                 .format(path, e.errno, e.strerror))
            sys.exit(1)


    def pipe_upload(self, filename):
        """
        Pipe the uploaded xtrabackup to a file

        """
        with open(filename, 'wb') as f:
            self.logger.debug("Uploading backup into {0}".format(filename))
            bs = self.config['read_size']
            while 42:
                data = sys.stdin.read(bs)
                f.write(data)
                if len(data) < bs:
                    break
            sys.stdin.close()


def receive_backup(config, logger, session, ip):
    """
    A simple wrapper to use SupraReceive class

    """
    receiver = SupraReceive(config, logger, session)
    receiver.receive(ip)
