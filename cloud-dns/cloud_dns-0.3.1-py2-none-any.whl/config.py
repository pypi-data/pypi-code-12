# encoding utf-8

from contextlib import closing, contextmanager
import logging
import os
import os.path as osp
import shutil
import subprocess
import sys
import tempfile
import urllib2

import boto
from boto.pyami.config import Config
import gcs_oauth2_boto_plugin
from keybase import keybase
import yaml

from .project import Project

DEFAULT_CONFIG_PATH = osp.expanduser('~/.config/cloud-dns')

@contextmanager
def temp_dir(**kwargs):
    """Utility function to create / destroy a temporary
    directory in a `with` statement
    """
    tmp_dir = tempfile.mkdtemp(**kwargs)
    logging.debug("Created temporary directory: " + tmp_dir)
    try:
        yield tmp_dir
    finally:
        if not os.environ.get('KEEP_TMPDIR'):
            logging.debug("Removing temporary directory: " + tmp_dir)
            shutil.rmtree(tmp_dir)


class Profiles(object):
    """Profiles container
    """
    def __init__(self, config_path=None, **kwargs):
        """
        :param config_path: configuration directory, default is ~/.config/cloud-dns
        """
        self.__config_path = config_path or DEFAULT_CONFIG_PATH

    def list(self):
        """Enumerate available profiles in config directory
        :return generator of `Profile` instance
        """
        for profile in os.listdir(self.__config_path):
            yield Profile(profile, config_path=self.__config_path)


class Profile(object):
    """Profile mainly hold a set of projects, having a set of nodes
    """
    def __init__(self, name, config_path=None, **kwargs):
        """
        :param name: the profile name (directory name in config root directory)
        :param config_path: config root directory, default is ~/.config/cloud-dns
        """
        self.__config_path = config_path or DEFAULT_CONFIG_PATH
        self.__name = name
        self.load_profile()

    @classmethod
    def profile_path(cls, name, config_path=None):
        """Provide absolute path to a profile configuration

        :param name: profile name
        :param config_path: config root directory
        """
        config_path = config_path or DEFAULT_CONFIG_PATH
        return osp.join(config_path, name)

    projects = property(
        fget=lambda slf: slf.__get_projects(),
        doc='Projects accessor'
    )

    keybase_users = property(
        fget=lambda slf: slf.__keybase_users,
        doc='Keybase users accessor'
    )

    name = property(
        fget=lambda slf: slf.__name,
        doc='Profile name read-only accessor'
    )

    path = property(
        fget=lambda slf: Profile.profile_path(slf.__name, slf.__config_path),
        doc='Read-only access to profile path'
    )

    config_path = property(
        fget=lambda slf: slf.__config_path,
        doc='Read-only accessor to the root configuration directory'
    )

    def __get_projects(self):
        if not any(self.__projects):
            for project, settings in self.__projects_settings.items():
                self.__projects[project] = Project(project, **settings)
        return self.__projects

    def write_dns_file(self, ostr):
        for project in self.projects.values():
            project.write_dns_file(ostr)


    def load_profile(self):
        if osp.isdir(self.path):
            with open(osp.join(self.path, 'projects.yml')) as istr:
                self.__projects = {}
                self.__projects_settings = {}
                for project, settings in yaml.load(istr).items():
                    if not osp.isabs(settings['pem_file']):
                        settings['pem_file'] = osp.join(self.path, settings['pem_file'])
                    self.__projects_settings[project] = settings
            with open(osp.join(self.path, 'users.yml')) as istr:
                self.__keybase_users = list(map(lambda id_: id_.split('://', 1), yaml.load(istr)))

class GSDriver(object):
    """Put and get from a Google Storage bucket.
    Assume public read access.
    Push is made with boto library. The boto configuration may be provided
    in the profile configuration
    """
    def __init__(self, profile):
        """
        :param profile: instance of `Profile`
        """
        boto_config = osp.join(profile.path, 'gstorage.boto')
        if osp.isfile(boto_config):
            boto.config = Config(path=boto_config)
            # patch config to have absolute path to p12 key
            p12_key_file = boto.config.get('Credentials', 'gs_service_key_file')
            p12_key_file = osp.expanduser(p12_key_file)
            if not osp.isabs(p12_key_file):
                p12_key_file = osp.join(profile.path, p12_key_file)
            boto.config.set('Credentials', 'gs_service_key_file', p12_key_file)

    def get(self, bucket, object):
        """Retrieve a file from a public Google Storage bucket

        :param bucket: Google Storage bucket name
        :param object: Path to file to retrieve, example: "/foo/bar.txt"
        :return file like instance
        """
        url = "https://{}.storage.googleapis.com{}".format(bucket, object)
        logging.info("Downloading file: " + url)
        return urllib2.urlopen(url)

    def put(self, bucket, obj, local_file):
        """Write a file to a Google Storage bucket

        :param bucket: Google Storage bucket name
        :param obj: Destination path to the file to write
        :param local_file: file like instance to read from
        """
        dst_uri = boto.storage_uri(bucket + obj, 'gs')
        logging.info("Uploading file to gs://{}{}".format(bucket, obj))
        dst_uri.new_key().set_contents_from_file(local_file)


class GStorageKeybaseProfile(Profile):
    """A profile able to pull and push its configuration to a Google Storage bucket
    """
    def __init__(self, name, gsdriver_cls, gsbucket,
                 keybase_id=None, config_path=None, **kwargs):
        """
        :param name: profile name

        :param gsdriver_cls: Class used to download / upload file to the
        Google Storage bucket

        :param keybase_id: keybase tuple identifier, for example ("github", "tristan0x")
        Used to download the proper encrypted file on Google Storage

        :param config_path: configuration root directory
        """
        super(GStorageKeybaseProfile, self).__init__(name, config_path)
        self.__gsbucket = gsbucket
        self.__keybase_id = keybase_id
        self.__gsdriver_cls = gsdriver_cls

    def gs_object(self, keybase_id=None):
        """Get the bucket path to the encrypted file to retrieve

        :param keybase_id: keybase tuple identifier, for example ("github", "tristan0x")
        :rtype string
        """
        keybase_id = keybase_id or self.__keybase_id
        return '/{}/{}-{}.gpg'.format(self.name, *keybase_id)

    def pull(self):
        """Update local profile with the one stored on Google Storage
        Careful: this will overwrite your existing configuration
        """
        with temp_dir() as tmp_dir:
            gstorage = self.__gsdriver_cls(self)
            gpg_file = osp.join(tmp_dir, self.name + '.tar.bz2.gpg')
            try:
                with closing(gstorage.get(self.__gsbucket, self.gs_object())) as remote_file, \
                     open(gpg_file, 'wb') as fp:
                    shutil.copyfileobj(remote_file, fp)
            except urllib2.HTTPError as ex:
                if ex.code == 404:
                    logging.error("Could find encryted profile on Google Storage for keybase identity: {}://{}".format(*self.__keybase_id))
                    logging.error("Please double-check identity or ask administrators to provide an encryted file for this identity")
                raise
            subprocess.check_call(
              "cat {} | gpg --decrypt | tar -C {} -jxf -".format(
                gpg_file, tmp_dir
            ), shell=True)
            decrypted_config = osp.join(tmp_dir, self.name)
            backup_config = osp.join(tmp_dir, self.name + '.prev')
            assert osp.isdir(decrypted_config)
            if osp.isdir(self.path):
                logging.debug("Moving profile in {}".format(backup_config))
                shutil.move(self.path, backup_config)
            elif not osp.isdir(osp.dirname(self.path)):
                logging.debug("Creating directories: " + osp.dirname(self.path))
                os.makedirs(osp.dirname(self.path))
            logging.debug("Copying new profile to: " + self.path)
            shutil.copytree(
                decrypted_config,
                self.path
            )
        self.load_profile()

    def push(self):
        """Push the local profile to Google Storage"""
        with temp_dir() as tmp_dir:
            logging.debug("Copying {} project configuration to {}"\
                .format(self.name, osp.join(tmp_dir, osp.basename(self.path))))
            shutil.copytree(self.path, osp.join(tmp_dir, osp.basename(self.path)))
            logging.debug("Compressing {} project configuration".format(self.name))
            subprocess.check_call('tar -C "{0}" -jcf "{0}/{1}.tar.bz2" "{1}"'.format(tmp_dir, self.name), shell=True)
            with open(osp.join(tmp_dir, self.name + '.tar.bz2'), 'rb') as istr:
                bz2_config = istr.read()
            work_dir = osp.join(tmp_dir, 'work')
            os.makedirs(work_dir)
            for idtype, id_ in self.keybase_users:
                users = keybase.discover(idtype, [id_])
                if any(users):
                    if len(users) > 1:
                        raise RuntimeError("More than once candidate for keybase user {}/{} ... weird"\
                            .format(idtype, ids))
                    logging.info("Encrypting {} project configuration for {}://{}".format(self.name, idtype, id_))
                    with open(osp.join(work_dir, osp.basename(self.gs_object((idtype, id_)))), 'wb') as ostr:
                        ostr.write(users[0].encrypt(bz2_config))
                else:
                    raise RuntimeError("Could not find keybase user {}/{}"\
                        .format(idtype, id_))
            gstorage = self.__gsdriver_cls(self)
            for idtype, id_ in self.keybase_users:
                with open(osp.join(work_dir, osp.basename(self.gs_object((idtype, id_)))), 'rb') as istr:
                    gstorage.put(
                        self.__gsbucket,
                        self.gs_object((idtype, id_)),
                        istr
                    )
