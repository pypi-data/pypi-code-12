# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Module :mod:`murdock.runner.runner`
-----------------------------------

Provides the Murdock runtime configuration class :class:`Configuration` and the
base class :class:`Runner` for the different types of Murdock runners
:class:`~murdock.runner.training.Docking,
`:class:`~murdock.runner.training.Screening` and
:class:`~murdock.runner.training.Training`.

:copyright: Copyright 2016 Malte Lichtner
:license: Apache License, Version 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import importlib
import json
import logging
import os
import shutil
import traceback

from murdock import CRASH_MESSAGE
import murdock.misc
import murdock.moldata
import murdock.report.latex
import murdock.report.sphinx


log = None


class MurdockInterrupt(Exception):
    pass


class MurdockTerminate(Exception):
    pass


class ConfigurationError(Exception):
    pass


class Configuration(object):
    """A class to handle the runtime configuration for Murdock.

    Parses and validates the command-line and configuration file and sets up
    one of the Murdock runners :class:`~murdock.runner.training.Docking,
    `:class:`~murdock.runner.training.Screening` or
    :class:`~murdock.runner.training.Training`.

    Usage Example:
        Import modules, create a :class:`Cofiguration` instance, parse the
        command-line, create a logger and validate the command-line options
        given::

            import logging
            import sys

            from murdock.logging import Logger
            from murdock.runner import Configuration

            cfg = Configuration()
            cfg.parse_command_line()
            log = Logger(
                file_level=cfg.log_file_level,
                console_level=cfg.log_console_level).logger
            cfg.setup_logger(filename='runner-example.log')
            if not cfg.validate_command_line():
                log.fatal('Error in command-line.')
                sys.exit(1)

        Parse and validate configuration file and setup Murdock runner::

            if not cfg.parse_configfile():
                log.fatal(
                    'Error in configuration file `%s`.', cfg.cmdline.config)
                sys.exit(1)
            setup = cfg.setup()

        Run Murdock::

            if setup.run(
                    file_level=cfg.log_file_level,
                    console_level=cfg.log_console_level):
                log.info('Murdock finished successful.')
                sys.exit(0)
            else:
                log.error('Murdock finished with errors.')
                sys.exit(1)


    Command-line Arguments and the Configuration File:
        The command-line arguments for Murdock are those options which do not
        affect the result of a docking/screening (output directories, logging,
        number of CPUs, ...). They are parsed, validated and stored in
        :meth:`~Configuration.parse_command_line()` using the `argparse
        <http://docs.python.org/dev/library/argparse.html>`_ module from the
        standard library (Python 2.7 and above). Starting Murdock with the
        argument ``--help`` gives a full list of command-line arguments with
        short descriptions.

        All settings affecting the result of a docking/screening are given in a
        single JSON-style input file. A description of the file structure, a
        full list of the available options and some examples are given in the
        :ref:`Usage <config>` section.

    Logging:
        The command-line arguments include options for logging. To account for
        those settings, a new logger for this module should be created using
        :meth:`Configuration.setup_logger()` right after a successful
        command-line validation.

    Parsing and Validation of the Configuration File:
        The configuration file is parsed and validated by calling
        :meth:`~Configuration.parse_configfile()`, which first parses the JSON
        file (using the `json <http://docs.python.org/library/json.html>`_
        module from the standard library) and then calls
        :meth:`~Configuration._validate()`.  The latter iterates through the
        configuration file recursively and checks each dictionary for the
        correct items.

        As the configuration options are defined within different modules (in
        the corresponding methods of the `ConfigDeclaration` classes), the
        function :func:`_get_options` is used to locate the correct module in
        three steps, returning the options as soon as they are found:

            1) First, the parent dictionary is checked for an item named
               ``"module"``.  If it exists, the options are expected in the
               module defined there. An example is the item ``"parameters"`` in
               the parent item ``"search"`` which also contains an entry
               defining the search module to be used, e.g.
               ``"module":"search.ps"``. Options expected in ``"parameters"``
               are then found in
               :meth:`murdock.search.ps.ConfigDeclaration.parameters`.

            2) Now, the module in which the item itself was defined is checked.
               The dictionary ``"receptor"``, for example, is itself an item of
               the dictionary ``"docking"`` and defined in the method
               :meth:`murdock.runner.docking.ConfigDeclaration.docking`. Its
               own options are found in the same module
               (:meth:`murdock.runner.docking.ConfigDeclaration.receptor`).

            3) At last (and quite often), the options are found in a Murdock
               module named just like the configuration item itself. Examples
               are the items ``"screening"``, ``"docking"`` and
               ``"transforms"``, whose options are defined in the corresponding
               modules :mod:`murdock.runner.screening`,
               :mod:`murdock.runner.docking` and :mod:`murdock.transforms`. For
               convenience the items ``"search"`` and ``"scoring"`` are linked
               to the modules :mod:`murdock.search` and :mod:`murdock.scoring`.

    Docking/Screening/Training Setup:
        After the successful validation of the command-line and the
        configuration file, the :attr:`Configuration.mode` is set to either
        ``'docking'`` or ``'screening'`` and :meth:`Configuration.setup()` is
        called. It sets up a :class:`~murdock.runner.docking.Docking` or
        :class:`~murdock.runner.screening.Screening` corresponding to the
        configuration and returns it. Both can be set up using their
        ``setup()`` methods (:meth:`murdock.runner.docking.Docking.setup()` and
        :meth:`murdock.runner.screening.Screening.setup()`) and started using
        their ``run()`` method (:meth:`murdock.runner.docking.Docking.run()`
        and :meth:`murdock.runner.screening.Screening.run()`).

    """

    def __init__(self):
        #: ArgumentParser object holding command line arguments
        self.cmdline = None
        #: dictionary holding the configuration information from the input file
        self.content = None
        #: path to the configuration file
        self.filepath = None
        #: log level for console output
        self.log_console_level = None
        #: log level for file output
        self.log_file_level = None
        #: working mode (``'docking'`` or ``'screening'``)
        self.mode = None
        #: list of strings pointing to the current JSON element validated, e.g.
        #: ['screening', 'input_data', 'item 3', 'receptor']
        self.json_location = []

    def parse_command_line(self):
        """Parse, validate and return command line arguments.
        """
        cmdline_parser = argparse.ArgumentParser(
            description='Murdock v%s - Python-based molecular docking' %
            murdock.__version__, epilog='Murdock configuration files may be '
            'either a) written manually or b) created using the command-line '
            'tool `murdock-config`. Please refer to the Murdock documentation '
            'for more information.')
        cmdline_parser.add_argument(
            'config', type=str, help='Murdock configuration file')
        cmdline_parser.add_argument(
            '--debug', action='store_true', help='write debug messages to '
            'log file (may result in large files)')
        cmdline_parser.add_argument(
            '-d', '--dry', action='store_true', help='perform a dry run '
            '(verify configuration, analyse input data, create Sphinx '
            'project; then skip the actual docking)')
        cmdline_parser.add_argument(
            '-l', '--log-to-console', action='store_true', help='print '
            'primary log to console')
        cmdline_parser.add_argument(
            '-L', '--latex-executable', required=False, type=str,
            help='PDFLaTeX executable (usually named `pdflatex`) for '
            'automated building of the PDF report')
        cmdline_parser.add_argument(
            '-o', '--output-formats', required=False, type=str, nargs='+',
            help='list of output formats for docked structures (default: '
            'input format)')
        cmdline_parser.add_argument(
            '-p', '--processes-per-screening', required=False, type=int,
            default=1, help='number of dockings started in parallel CPU '
            'processes')
        cmdline_parser.add_argument(
            '-P', '--pymol-executable', required=False, type=str,
            help='PyMOL executable for automated PNG picture creation')
        cmdline_parser.add_argument(
            '--pymol-script', required=False, type=str,
            help='PyMOL script to be run during PNG picture creation')
        cmdline_parser.add_argument(
            '--residue-distance-charts', action='store_true', help='draw '
            'residue distance charts for each docking (may result in many '
            'small files)')
        cmdline_parser.add_argument(
            '--residue-score-charts', action='store_true', help='draw '
            'residue score charts for each docking (may result in many small '
            'files)')
        cmdline_parser.add_argument(
            '-r', '--restore', action='store_true', help='resume an aborted '
            'docking or screening using docked structures found in the '
            '`docked/` directories')
        cmdline_parser.add_argument(
            '--result-directory', required=False, type=str,
            help='directory for result files (default: current working '
            'directory)')
        cmdline_parser.add_argument(
            '--resume', required=False, action='store_true', help='resume an '
            'aborted docking or screening using docked structures found in '
            'the `docked/` directories and all results found in '
            '`*-results.json` files')
        cmdline_parser.add_argument(
            '--reverse', action='store_true', help='reverse order of '
            'dockings given in configuration file')
        cmdline_parser.add_argument(
            '--sampling', required=False, action='store_true', help='record '
            'sampling data for each type of transformation (may result in '
            'large files)')
        cmdline_parser.add_argument(
            '-S', '--sphinx-executable', required=False, type=str,
            help='Sphinx executable (usually named `sphinx-build`) for '
            'automated building of the HTML report')
        cmdline_parser.add_argument(
            '-t', '--threads-per-docking', required=False, type=int,
            help='number of CPU threads used for each docking process (sets '
            'the environment variables OMP_NUM_THREADS and MKL_NUM_THREADS; '
            'default: unlimited)')
        cmdline_parser.add_argument(
            '-u', '--update-interval', required=False, type=int, default=1,
            help='time interval between two screening result updates in '
            'seconds (default: 1)')
        cmdline_parser.add_argument(
            '--version', action='version', version=murdock.__version__)
        self.cmdline = cmdline_parser.parse_args()
        cl = self.cmdline
        cl.config = os.path.expandvars(os.path.expanduser(cl.config))
        if cl.result_directory is not None:
            cl.result_directory = os.path.expandvars(
                os.path.expanduser(cl.result_directory))
        else:
            if cl.resume:
                cl.result_directory = os.path.normpath(
                    os.path.join(os.path.dirname(cl.config), '../'))
            else:
                cl.result_directory = '.'
        if cl.pymol_script is not None:
            cl.pymol_script = os.path.expandvars(os.path.expanduser(
                cl.pymol_script))
        if cl.debug:
            self.log_file_level = logging.DEBUG
        else:
            self.log_file_level = logging.INFO
        if cl.log_to_console:
            self.log_console_level = logging.INFO
        else:
            self.log_console_level = None
        return True

    def parse_configfile(self):
        """Parse and validate the JSON configuration file.
        """
        self.filepath = self.cmdline.config
        log.info('Parse configuration file `%s`.', self.filepath)
        try:
            self.content = murdock.misc.load_ordered_json(self.filepath)
        except IOError:
            log.fatal('Configuration file `%s` does not exist.', self.filepath)
            return False
        except ValueError:
            log.fatal(
                'File `%s` is not a valid JSON file. Check JSON format '
                'specification (http://www.json.org). %s', self.filepath,
                traceback.format_exc().splitlines()[-1])
            return False
        self.mode = list(self.content)[0]
        if len(self.content) == 1 and self.mode in (
                'docking', 'screening', 'training'):
            self.json_location.append(self.mode)
            return self._validate(
                section=self.mode, items=self.content[self.mode])
        else:
            log.fatal(
                'Configuration file must contain exactly one top level key: '
                '`docking`, `screening` or `training`.')
        return False

    def setup(self):
        """Setup screening or docking and return it ready to run.
        """
        cl = self.cmdline
        content = self.content[self.mode]
        if 'label' not in content:
            content['label'] = os.path.splitext(
                os.path.basename(self.filepath))[0]
        label = content['label']
        if 'title' not in content:
            content['title'] = label
        titledir = os.path.join(cl.result_directory, label)
        cfg_filepath = os.path.join(titledir, '%s-config.json' % label)
        if not cl.resume and not cl.restore:
            if os.path.exists(titledir):
                log.fatal(
                    'There is already a directory called `%s` in the '
                    'designated results directory `%s`. Please use an empty '
                    'directory for results output.', titledir,
                    cl.result_directory)
                return False
            os.makedirs(titledir)
            with codecs.open(cfg_filepath, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.content, indent=2))
            log.info(
                'Copy of configuration file written to `%s`.', cfg_filepath)
        elif not os.path.exists(titledir):
            log.fatal(
                'The results directory of the Murdock project to be '
                'resumed/restored can not be found. Based on the path of the '
                'configuration file given, the results directory is expected '
                'to be found at `%s`. Please choose the copy of the original '
                'configuration file found in the results directory of the '
                'Murdock project you want to resume/restore.',
                os.path.abspath(titledir))
            return False
        if cl.output_formats is not None:
            cl.output_formats = [
                _fmt if _fmt.startswith('.') else '.%s' % _fmt for _fmt in
                cl.output_formats]
            for fmt in cl.output_formats:
                if not murdock.moldata.get_backend_module(fmt):
                    log.error(
                        'Unknown file extension `%s` for '
                        '`-o/--output-formats`. Known extensions are: %s. '
                        'Lists are allowed, e.g. `-o .pdb .mol2`.', fmt,
                        ', '.join(murdock.moldata.known_extensions()))
                    return False
        log.info('Setup %s configuration.', self.mode)
        # Remove default item in `steps` if present.
        for dat in content['steps']:
            if dat['title'] == 'default':
                content['steps'].remove(dat)
                break
        if 'notes' in content:
            notes = content['notes']
        else:
            notes = None
        try:
            user = content['user']
        except KeyError:
            user = None
        # Create report projects.
        report_modules = [murdock.report.sphinx, murdock.report.latex]
        build_execs = {
            murdock.report.sphinx: cl.sphinx_executable,
            murdock.report.latex: cl.latex_executable}
        kwargs = {
            murdock.report.sphinx: {
                'outdir': os.path.join(titledir, 'sphinx')},
            murdock.report.latex: {
                'outdir': os.path.join(titledir, 'latex')}}
        report_projects = [
            _module.Project(
                mode=self.mode.capitalize(), title=content['title'],
                label=content['label'], user=user,
                build_exec=build_execs[_module], **kwargs[_module]) for
            _module in report_modules]
        for project in report_projects:
            if os.path.exists(project.outdir):
                log.debug('Clear project directory `%s`.', project.outdir)
                shutil.rmtree(project.outdir)
            project.create()
            if project.build_exec is not None:
                project.create_symlink(titledir)
        # Set up docking steps
        dsteps = _setup_steps(content)
        # Check preprocessing section.
        try:
            preprocessing = content['preprocessing']
        except KeyError:
            preprocessing = None
        main_kwargs = {
            'label': content['label'], 'title': content['title'],
            'moldata': content['input_data'], 'resdir': titledir,
            'notes': notes}
        docking_kwargs = {
            'docking_steps': dsteps, 'restore': cl.restore,
            'resume': cl.resume, 'num_runs': content['number_of_runs'],
            'preprocessing': preprocessing, 'dry': cl.dry,
            'report_projects': report_projects,
            'debugsampling': cl.sampling, 'pymolexec': cl.pymol_executable,
            'pymolscript': cl.pymol_script,
            'num_threads': cl.threads_per_docking,
            'failmode': content['fail-mode'],
            'draw_resscore_charts': cl.residue_score_charts,
            'draw_resdist_charts': cl.residue_distance_charts,
            'outfmts': cl.output_formats}
        if self.mode == 'docking':
            if cl.processes_per_screening != 1:
                log.fatal(
                    'The command-line argument `-p/--processes-per-screening` '
                    'enables multiprocessing only for screenings, where each '
                    'docking is run in a seperate process and can not be used '
                    'for a single docking setup. Use the command-line '
                    'argument `-t/--threads-per-docking` to enable '
                    'multithreading for Numpy/Scipy operations instead (and '
                    'make sure your Python/Numpy/Scipy build supports this '
                    'feature.')
                return False
            if cl.reverse:
                log.fatal(
                    'The command-line argument `--reverse` reverses the order '
                    'in which dockings are started in a screening. It has no '
                    'effect for a single docking.')
                return False
        elif self.mode in ('screening', 'training'):
            for dat in content['input_data']:
                if dat['title'] == 'default':
                    content['input_data'].remove(dat)
                    break
            if cl.processes_per_screening > len(content['input_data']):
                log.warning(
                    'The command-line argument `-p/--processes-per-screening` '
                    'is set to %d which is more than the number of '
                    'independent dockings set up in the configuration file '
                    '`%s`. Only %d processes will be started.',
                    cl.processes_per_screening, cl.config,
                    len(content['input_data']))
            for report_project in report_projects:
                for d in content['input_data']:
                    report_project.add_document(d['label'])
            screening_kwargs = {
                'num_procs': cl.processes_per_screening, 'reverse': cl.reverse,
                'update_interval': cl.update_interval}
        # Setup docking.
        if self.mode == 'docking':
            kwargs = dict(
                list(main_kwargs.items()) + list(docking_kwargs.items()))
            return murdock.runner.docking.Docking(**kwargs)
        # Set up screening.
        elif self.mode == 'screening':
            kwargs = dict(
                list(main_kwargs.items()) + list(screening_kwargs.items()) +
                list(docking_kwargs.items()))
            return murdock.runner.screening.Screening(**kwargs)
        elif self.mode == 'training':
            training_kwargs = {
                'raster': content['raster'], 'term_kwargs': content['terms']}
            kwargs = dict(
                list(main_kwargs.items()) + list(training_kwargs.items()) +
                list(screening_kwargs.items()) + list(docking_kwargs.items()))
            return murdock.runner.training.Training(**kwargs)
        raise ConfigurationError(
            'The mode `%s` is unknown. Allowed are `docking`, `screening` and '
            '`training`.' % self.mode)

    def setup_logger(self, filename, file_level=logging.INFO):
        """Set up logger with consideration of command-line arguments.
        """
        if self.log_console_level is not None:
            console_level = logging.INFO
        else:
            console_level = None
        global log
        log = murdock.logger.Logger(
            name='config', file_level=file_level,
            logdir=self.cmdline.result_directory, filename=filename,
            console_level=console_level).logger
        return True

    def validate_command_line(self):
        cl = self.cmdline
        log.info('Command-line arguments:')
        for cmd, val in sorted(list(self.cmdline.__dict__.items())):
            cmdstr = ' '.join(cmd.split('_'))
            log.info('  %s: %s', cmdstr, str(val))
        # Configure multithreading.
        for varname in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
            var = os.getenv(varname)
            if cl.threads_per_docking is not None:
                if var and var != '%d' % cl.threads_per_docking:
                    log.info(
                        'The environment variable `%s` was set to %s and is '
                        'now changed based on the command-line argument '
                        '`-t/--threads-per-docking`.', varname, var)
                os.environ[varname] = '%d' % cl.threads_per_docking
                log.info(
                    'Set the environment variable `%s` to %d.', varname,
                    cl.threads_per_docking)
            elif var:
                log.info(
                    'The environment variable `%s` is set to %s and '
                    'limits the number of threads used by Numpy/Scipy '
                    'operations. If required, use the command-line argument '
                    '`-t/--threads-per-docking` to a) set the environment '
                    'variable on runtime and b) force external applications '
                    '(such as PyMOL) to use the same number of threads.',
                    varname, var)
        # Resume an existing project.
        if cl.resume or cl.restore:
            titledir = os.path.abspath(os.path.dirname(cl.config))
            resdir = os.path.abspath(os.path.join(titledir, '../'))
            if os.path.abspath(cl.result_directory) != resdir:
                log.fatal(
                    'If the command-line arguments `-r/--restore` or '
                    '`--resume` are given, Murdock determines the existing '
                    'results directory structure based on the path of the '
                    'configuration file. Please choose the configuration file '
                    'Murdock has automatically created within the existing '
                    'results directory (`<label>-config.json`). For the '
                    'configuration file `%s` given, the working directory is '
                    'expected to be `%s` and new results would be merged with '
                    'results found in `%s`.', os.path.abspath(cl.config),
                    resdir, titledir)
                return False
        if cl.processes_per_screening <= 0:
            log.fatal(
                'Argument `-p/--processes-per-screening` must be a number '
                'greater than zero.')
            return False
        return True

    def _check_subsection(self, option, items, module):
        if (
                option.dtype in (dict, list) and option.length is not None and
                len(items[option.name]) != option.length):
            log.fatal(
                '%sThere are %d items given but %d are required.',
                self._get_err_str(), len(items[option.name]), option.length)
            return False
        if option.dtype is dict:
            if not self._validate(
                    section=option.name, items=items[option.name],
                    module=module):
                return False
        if option.dtype is list:
            if not self._validate_list(
                    section=option.name, items=items[option.name],
                    module=module):
                return False
        return True

    def _get_err_str(self):
        return 'Error in section [%s]: ' % ' -> '.join(self.json_location)

    def _validate(self, section, items, module=None, default_item=None):
        """Validate all `items` within a `section` recursively.

        There is a number of checks performed on each `section` and its items.
        Ways the validation can fail include:

            a) No configuration options are declared for a section or no
               declaration can be found.

            b) A declared option is missing in the configuration file even
               though it is required, has no default value and there is no
               corresponding default item.

            c) There is an unknown item in the configuration file which is not
               found in the deklaration of this `section`.

            d) An item value in the configuration file has a different type
               than the declared option.
        """
        module, options = _get_options(section, module)
        if not options:
            log.fatal(
                '%sConfiguration declaration for section `%s` can not be '
                'located.', self._get_err_str(), section)
            return False
        if 'module' in items:
            try:
                mod = murdock.misc.get_python_module(items['module'])
            except ImportError:
                log.fatal(
                    '%sModule `murdock.%s` does not exist.',
                    self._get_err_str(), items['module'])
                return False
            except:
                log.fatal(
                    '%sImport of module `murdock.%s` failed. Check module log '
                    'or traceback for more information.', self._get_err_str(),
                    items['module'])
                log.fatal(traceback.format_exc())
                return False
            if 'function' in items and not murdock.misc.get_python_function(
                    mod, items['function']):
                log.fatal(
                    '%sThe python function `%s.%s` does not exist.',
                    self._get_err_str(), mod.__name__, items['function'])
                return False
        elif 'function' in items:
            log.fatal(
                '%sThe item `function` (`%s`) is given without the '
                'corresponding `module` which is required.',
                self._get_err_str(), items['function'])
            return False
        _set_label(items)
#         if not options:
#             # This should only occur for custom functions not requiring the
#             # option `arguments`.
#             module = murdock.config
#             options = module.ConfigDeclaration().get_default_options()
        for opt in options:
            self.json_location.append(opt.name)
            if opt.name not in items:
                if (default_item is not None and opt.name in default_item and
                        opt.name != 'title'):
                    items[opt.name] = default_item[opt.name]
                elif opt.default is not None:
                    items[opt.name] = opt.default
                else:
                    if not opt.required or (
                            'title' in items and items['title'] == 'default'):
                        self.json_location.pop()
                        continue
                    else:
                        log.fatal(
                            '%sRequired configuration item `%s` (%s) not '
                            'found.', self._get_err_str(), opt.name,
                            opt.description)
                        return False
            if opt.choices is not None and items[opt.name] not in opt.choices:
                log.fatal(
                    '%sConfiguration item `%s` (%s) has the value `%s` but '
                    'only the following choices are allowed: %s.',
                    self._get_err_str(), opt.name, opt.description,
                    items[opt.name], ', '.join(opt.choices))
                return False
            try:
                opt.dtype(items[opt.name])
            except (ValueError, TypeError):
                log.fatal(
                    '%sConfiguration item `%s` (%s) has type `%s`, '
                    'required is `%s`.', self._get_err_str(), opt.name,
                    opt.description, type(items[opt.name]).__name__,
                    opt.dtype.__name__)
                return False
            if opt.check_filepath:
                items[opt.name] = os.path.expandvars(os.path.expanduser(
                    items[opt.name]))
                if not os.path.exists(items[opt.name]):
                    log.fatal(
                        '%sFile `%s` (%s) does not exists.',
                        self._get_err_str(), items[opt.name], opt.description)
                    return False
                # Expand environment variables within all input paths.
                items[opt.name] = os.path.expandvars(os.path.expanduser(
                    items[opt.name]))
            if (opt.dtype is dict or opt.dtype is list) and opt.validate:
                if not isinstance(items[opt.name], opt.dtype):
                    log.fatal(
                        '%sConfiguration item `%s` (%s) has type `%s`, '
                        'required is `%s`.', self._get_err_str(), opt.name,
                        opt.description, type(items[opt.name]).__name__,
                        opt.dtype.__name__)
                    return False
                if 'module' in items:
                    mod = murdock.misc.get_python_module(items['module'])
                else:
                    mod = module
                if not self._check_subsection(
                        option=opt, items=items, module=mod):
                    return False
            self.json_location.pop()
        for item in items:
            if item not in (_opt.name for _opt in options):
                log.fatal(
                    '%sUnknown configuration item `%s`.', self._get_err_str(),
                    item)
                return False
        return True

    def _validate_list(self, section, items, module=None):
        """Iterate through a configuration list and validate its elements.
        """
        default_item = None
        uniques = {'label': [], 'title': [], 'name': []}
        for i, item in enumerate(items):
            self.json_location.append(
                'item %d%s' % (i + 1, _labellike(item)))
            # Check for a default item.
            if 'title' in item and item['title'] == 'default':
                if default_item is not None:
                    log.fatal(
                        '%sMultiple default items found.', self._get_err_str())
                    return False
                default_item = item
            # Check for unique labels, titles and names
            for key in (_k for _k in uniques if _k in item):
                if item[key] in uniques[key]:
                    log.fatal(
                        '%sMultiple elements with the same label/name/title '
                        '`%s` found. Within a list, all '
                        '`label`/`name`/`title` attributes must be unique.',
                        self._get_err_str(), item[key])
                    return False
                uniques[key].append(item[key])
            self.json_location.pop()
        # recursively validate all list elements
        for i, item in enumerate(items):
            self.json_location.append(
                'item %d%s' % (i + 1, _labellike(item)))
            if not self._validate(
                    section=section, items=item, module=module,
                    default_item=default_item):
                return False
            self.json_location.pop()
        return True


class Runner(object):

    def __init__(
            self, logger, moldata, resdir='.', restore=False, resume=False,
            result_suffix='-results'):
        #: data on input molecular structures
        self.moldata = moldata
        #: result directory
        self.resdir = os.path.expanduser(resdir)
        if not os.path.exists(self.resdir):
            os.makedirs(self.resdir)
        #: parse existing docked structure files; perform only missing runs
        self.restore = restore
        #: suffix for result files
        self.result_suffix = result_suffix
        #: parse existing JSON result files; perform only missing runs
        self.resume = resume
        #: perform a full report and result update on next occasion
        self.update_full = True
        #: result container
        self.result = None
        #: formatted report
        self.report = None
        global log
        log = logger

    @property
    def json_filepath(self):
        return os.path.join(
            self.resdir, '%s%s.json' % (self.label, self.result_suffix))

    @property
    def label(self):
        return self.result.label

    @property
    def mode(self):
        return self.__class__.__name__.lower()

    @property
    def status(self):
        return self.result.status

    @property
    def title(self):
        return self.result.title

    def run(self, **kwargs):
        try:
            return self._setup(**kwargs) and self._run() and self._shutdown()
        except MurdockInterrupt:
            log.warning('Abort %s `%s`.', self.mode, self.title)
            self.result.set_status('aborted')
            self._shutdown()
            return False
        except MurdockTerminate:
            log.warning('Abort %s `%s` (quick)', self.mode, self.title)
            self.result.set_status('aborted')
            self._shutdown(quick=True)
            return False
        except:
            log.fatal(
                '%s `%s` crashed due to bad code. %s %s', self.mode,
                self.title, traceback.format_exc(), CRASH_MESSAGE)
            self.result.set_status('CRASHED')
            self._shutdown(quick=True)
            raise

    def _setup(self):
        raise NotImplementedError

    def _run(self):
        raise NotImplementedError

    def _shutdown(self, quick=False):
        raise NotImplementedError

    def _write_results(self):
        log.debug(
            'Create report for `%s` (%s).', self.label,
            'full' if self.update_full else 'update status')
        self.report.create(full=self.update_full)
        self.report.write()
        for b in self.report.backends:
            if b.project.build_exec:
                log.debug(
                    'Build report (`%s`).', b.project.get_build_link()[1])
                b.project.build()
        log.debug('Write results to `%s`.', self.json_filepath)
        with codecs.open(self.json_filepath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(
                {self.mode: self.result.to_json()}, sort_keys=False, indent=2))
        return True


def _get_options(section, module=None):
    """Try to find configuration options for `section` and return them.
    """
    options = False
    if module is not None:
        # look in current module
        options = _validate_declaration(module, section)
    if not options:
        # look for a module named after the section
        for loc in (['murdock'], ['murdock', 'runner']):
            try:
                module = importlib.import_module('.'.join(loc + [section]))
            except ImportError:
                continue
            break
        else:
            return False, False
        options = _validate_declaration(module, section)
    return module, options


def _labellike(item):
    if 'label' in item:
        return ' (`%s`)' % item['label']
    elif 'name' in item:
        return ' (`%s`)' % item['name']
    elif 'title' in item:
        return ' (`%s`)' % item['title']
    else:
        return ''


def _set_label(items):
    if 'label' in items:
        items['label'] = murdock.misc.cleanup_filename(items['label'])
    elif 'title' in items:
        items['label'] = murdock.misc.cleanup_filename(items['title'])
    elif 'name' in items:
        items['label'] = murdock.misc.cleanup_filename(items['name'])
    elif 'filepath' in items:
        items['label'] = os.path.splitext(os.path.basename(
            items['filepath']))[0]
    return True


def _validate_declaration(module, section):
    """Return options for `section` if they are declared in `module`.
    """
    try:
        return getattr(module.ConfigDeclaration(), section)()
    except AttributeError:
        return False


def _setup_steps(content):
    """Setup docking steps for a screening or a single docking.
    """
    dsteps = []
    for ind, s in enumerate(content['steps']):
        # Set python function filtering rotatable bonds.
        transform_parms = s['transforms']
        #: Create docking step.
        scoring_mod = murdock.misc.get_python_module(
            s['scoring']['module'])
        search_mod = murdock.misc.get_python_module(s['search']['module'])
        dstep = murdock.runner.docking.DockingStep(
            ind=ind, title=s['title'], transform_parms=transform_parms,
            scoring_module=scoring_mod,
            scoring_parms=s['scoring']['parameters'], search_module=search_mod,
            search_parms=s['search']['parameters'],
            write_intvideo=s['search']['intvideo'],
            write_extvideo=s['search']['extvideo'],
            store_decoy_scores=s['search']['store_decoy_scores'])
        dsteps.append(dstep)
    return dsteps
