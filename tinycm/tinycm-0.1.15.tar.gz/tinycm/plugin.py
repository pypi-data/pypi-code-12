import subprocess
import shutil
import logging


def install_plugin(name):
    logger = logging.getLogger('tinycm')

    package = "tinycm_{}".format(name)
    logger.info('Installing plugin {}'.format(package))

    pips = ['pip3.6', 'pip-3.6', 'pip3.5', 'pip-3.5', 'pip3.4', 'pip-3.4', 'pip3']
    the_good_pip = None

    for pip in pips:
        if shutil.which(pip):
            the_good_pip = pip
            break

    command = [the_good_pip, 'install', package]
    logger.debug('Running command: {}'.format(' '.join(command)))
    subprocess.check_call(command)
