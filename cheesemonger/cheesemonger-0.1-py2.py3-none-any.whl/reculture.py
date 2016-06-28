from __future__ import unicode_literals

import subprocess
import argparse
import shlex
from tempfile import mkdtemp
from os import listdir
from os.path import (join as pjoin,
        expandvars as expvars,
        expanduser as expusr)
import shutil
import json
import sys

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import Error as ConfigParserError
    from ConfigParser import SafeConfigParser as ConfigParser
    ConfigParser._old_get = ConfigParser.get
    def get_with_fallback(
            self, section, option, raw=False, vars=None, fallback=None
    ):
        try:
            return self._old_get(section, option, raw, vars)
        except ConfigParserError:
            return fallback
    ConfigParser.get = get_with_fallback

import logbook
from logbook.compat import redirect_logging
import distlib.wheel, distlib.metadata
from appdirs import user_cache_dir, user_config_dir
from venv_tools import TemporaryVenv, Venv

DEFAULT_INSTALL_COMMAND = "python -m pip install {package_specs}"
DEFAULT_WHEEL_BUILD_COMMAND = "python -m pip wheel --wheel-dir {output_dir} {package_specs}"
DEFAULT_CACHE_DIR = user_cache_dir(appname="cheesemonger-reculture")
DEFAULT_CONFIG_DIR = user_config_dir(appname="cheesemonger-reculture")
DEFAULT_CONFIG_FILE = pjoin(DEFAULT_CONFIG_DIR, "config.ini")
DEFAULT_METADATA_FILE = pjoin(DEFAULT_CONFIG_DIR, "default.json")
WHEEL_METADATA_PATH = "{name}-{version}.dist-info/metadata.json"

#redirect_logging()
log = logbook.Logger(__name__)

def find_matching_start_str(iterable, substr):
    for s in iterable:
        if s.lower().startswith(substr.lower()):
            return s


def install_setup_reqs(pkg_setup_reqs, install_command=DEFAULT_INSTALL_COMMAND):
    if pkg_setup_reqs:
        log.debug(subprocess.check_output(shlex.split(
            install_command.format(
                package_specs=" ".join(pkg_setup_reqs),
        ))))

def build_wheel(pkg, output_dir=".",
        wheel_command=DEFAULT_WHEEL_BUILD_COMMAND,
):
    try:
        log.debug(subprocess.check_output(shlex.split(
            wheel_command.format(
                package_specs=pkg,
                output_dir=output_dir,
        )), universal_newlines=True))
    except subprocess.CalledProcessError as e:
        print('\n'.join([
            "Wheel build of {pkg} failed.",
            "Command: {cmd}",
            "{output}"]).format(
                pkg=pkg,
                cmd=" ".join(e.cmd),
                output=e.output.replace("\\n", "\n")
        ))
        sys.exit(1)


def add_reqs_to_wheel(wheel, requirement_list):
    def wheel_updater(path_map, name=None, version=None, **kwargs):
        if requirement_list:
            if name is None:
                raise RuntimeError("Wheel must have a name")
            if version is None:
                raise RuntimeError("Wheel must have a version")
            metadata_file = path_map[WHEEL_METADATA_PATH.format(name, version)]
            metadata = distlib.metadata.Metadata(path=metadata_file)
            metadata.add_requirements(requirement_list)
            metadata.write(path=metadata_file)
        return True

    w = distlib.wheel.Wheel(wheel)
    w.update(
        wheel_updater, name=w.name, version=w.version
    )

def main():
    with logbook.StderrHandler().applicationbound():
        parser = argparse.ArgumentParser(
                description="Package cache builder with scientific python in mind"
                )

        parser.add_argument("packages", nargs="+")
        parser.add_argument(
                "--config",
                action="store",
                help="path to config file"
            )
        parser.add_argument(
                "--wheel-cache",
                action="store",
                help="path to store wheel cache"
            )
        parser.add_argument(
                "--package-requirements",
                action="store",
                help="path of package requirements"
            )
        parser.add_argument(
                "--python", "-p",
                action="store",
                help="path to python version to use",
                default=None
            )

        args = parser.parse_args()

        config_path = args.config or DEFAULT_CONFIG_FILE
        conf_parser = ConfigParser()
        conf_parser.read(config_path)

        cache_dir = (
                args.wheel_cache or
                expvars(expusr(conf_parser.get(
                    "paths", "wheel_cache",
                    fallback=DEFAULT_CACHE_DIR)
            )))

        req_path = (
                args.package_requirements or
                expvars(expusr(conf_parser.get("paths", "req_path",
                    fallback=DEFAULT_METADATA_FILE)
            )))

        with open(req_path) as f:
            req_mapping = json.load(f)

        requested_packages = args.packages

        for pkg in requested_packages:
            requested_packages.extend(req_mapping.get(pkg, []))

        log.info("python exe: {}".format(args.python))

        built_packages = []
        for pkg in reversed(requested_packages):
            if pkg not in built_packages:
                log.notice("Building {}".format(pkg))
                with TemporaryVenv(
                    use_virtualenv=True,
                    path_to_python_exe=args.python,
                    with_pip=True
                ) as venv, Venv(venv):
                    install_setup_reqs(["wheel"]) # pip cannot build wheels without it
                    install_setup_reqs(req_mapping.get(pkg, []))
                    tempdir = mkdtemp()
                    build_wheel(pkg, output_dir=tempdir)
                    wheels = listdir(tempdir)
                    log.debug("{} {}".format(tempdir, wheels))
                    wheel_file = find_matching_start_str(wheels, pkg)
                    add_reqs_to_wheel(
                            pjoin(tempdir, wheel_file),
                            req_mapping.get(pkg))
                    for f in wheels:
                        shutil.copy(pjoin(tempdir, f), cache_dir)
                    shutil.rmtree(tempdir)
                built_packages.append(pkg)
            else:
                log.info("{} already built".format(pkg))
                pass

if __name__ == '__main__':
    main()
