import os
import re
import subprocess
import socket
from generaltools import log_tools

log = log_tools.init_logger("system_tools", log_to_file=False)

def download_file(url, path_to_store):
    cmd = ["wget", url, path_to_store]
    subprocess.call(cmd)

def store_package_list(output_file=None):
    cmd = ["dpkg", "--get-selections"]
    package_list = subprocess.check_output(cmd)
    pattern = r"^.*(deinstall|hold|purge)\n"
    new_list = re.sub(pattern, '', package_list, flags=re.MULTILINE)
    pattern = r"\s*[^de]install$"
    new_list = re.sub(pattern, '', package_list, flags=re.MULTILINE)
    if output_file:
        with open(output_file, "w") as file_:
            log.debug("Storing package list to {}".format(file_))
            file_.write(new_list)
    else:
        return new_list.split("\n")

def add_package_to_list(package, list_):
    pattern = r"^{}$".format(package)
    with open(list_, "r") as file_:
        list_string = file_.read()
        package_present = re.search(pattern,
                                    list_string,
                                    flags=re.MULTILINE)
    with open(list_, "a") as file_:
        if not package_present:
            file_.write("{}\n".format(package))
            log.info("Package {} added to list".format(package))
        else:
            log.info("Package {} already in list".format(package))

def remove_package_from_list(package, list_):
    pattern = r"^{}\n".format(package)
    with open(list_, "r") as file_:
        list_string = file_.read()
        package_present = re.search(pattern,
                                    list_string,
                                    flags=re.MULTILINE)
    if package_present:
        with open(list_, "r") as file_:
            new_list = file_.read()
            new_list = re.sub(pattern, '', new_list, flags=re.MULTILINE)
        with open(list_, "w") as file_:
            file_.write(new_list)
        log.info("Package {} removed from the list.".format(package))
    else:
        log.info("Package {} was not included in the list.".format(package))

def install_package_list(list_):
    ''' Install all packages from a list of files

    This assumes a file generated with `dpkg --get-selections`
    '''
    installed_packages = store_package_list()
    with open(list_, "r") as packages:
        packages = packages.readlines()
        packages = [p.strip() for p in packages]
        packages_to_install = list(set(packages) - set(installed_packages))
        if len(packages_to_install) < 1:
            log.info("All requested packages are already installed")
            return None
        cmd = ["sudo", "apt-get", "-y", "install"] + packages_to_install
        log.debug(cmd)
        subprocess.call(cmd)

def upgrade_system():
    """Upgrade an Ubuntu installation"""
    cmd = ["sudo", "apt-get", "update"]
    subprocess.call(cmd)
    cmd = ["sudo", "apt-get", "-y", "upgrade"]
    subprocess.call(cmd)
