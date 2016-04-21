import os
import sys
import six
import uuid
import logging
import tarfile
import tempfile
import argparse
from oct_turrets.turret import Turret
from oct_turrets.exceptions import InvalidConfiguration, InvalidTarTurret
from oct_turrets.utils import validate_conf, clean_tar_tmp, load_file

log = logging.getLogger(__name__)


def unpack(turret_achive, dir_name):
    """Unpack the turret and add extract path to PYTHONPATH

    :param str unique_id: the unique turret identifier
    :return: False is there is a problem with the tarball, True otherwise
    :rtype: bool
    """
    if not tarfile.is_tarfile(turret_achive):
        return False
    with tarfile.open(turret_achive) as tar:
        tar.extractall(dir_name)
    sys.path.append(dir_name)
    return True


def from_tar(tar_path, unique_id, dir_name):
    """Load all require components from tar archive

    :param str tar_path: the path to json configuration file
    :param str unique_id: the unique identifier of the turret
    :param str dir_name: the full path for extraction
    :return: module file and loaded configuration
    """

    if not unpack(tar_path, dir_name):
        raise InvalidTarTurret("Invalide tar file provided")

    try:
        config = validate_conf(os.path.join(dir_name, 'config.json'))
    except InvalidConfiguration:
        clean_tar_tmp(dir_name, True)
        raise

    module_file = os.path.join(dir_name, config['script'])
    module = load_file(module_file)
    return module, config


def from_config(config_path):
    """Load all require components from configuration file

    :param str config_path: the path to json configuration file
    :return: module file and loaded configuration
    """
    config = validate_conf(config_path)
    cfg_path = os.path.dirname(config_path)
    module_file = os.path.join(cfg_path, config['script'])
    module = load_file(module_file)
    return module, config


def start(args):
    unique_id = six.text_type(uuid.uuid4())
    is_tar = None

    if args.tar is not None:
        dir_name = "{}-{}".format(os.path.basename(args.tar).split('.')[0], unique_id)
        dir_name = os.path.join(tempfile.gettempdir(), dir_name)
        module, config = from_tar(args.tar, unique_id, dir_name)
        is_tar = True
    else:
        module, config = from_config(args.config)

    turret = Turret(config, module, unique_id)

    try:
        turret.start()
    except (Exception, KeyboardInterrupt):
        clean_tar_tmp(dir_name, is_tar)
        raise

    clean_tar_tmp(dir_name, is_tar)


def main():

    parser = argparse.ArgumentParser(description='Give parameters for start a turret instance')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--config-file', type=str, default=None, help='path for json configuration file')
    group.add_argument('--tar', type=str, default=None, help='Path for the tarball to use')
    args = parser.parse_args()

    if args.config_file is None and args.tar is None:
        parser.error('You need a config_file.json to start a turret')

    start(args)
