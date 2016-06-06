#!/usr/bin/python
#
# Copyright (c) 2013 Mikkel Schubert <MSchubert@snm.ku.dk>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import os
import time
import logging
import optparse

import paleomix
import paleomix.pipeline
import paleomix.ui
import paleomix.yaml
import paleomix.logger

import paleomix.common.console as console
import paleomix.tools.bam_pipeline.makefile as makefile
import paleomix.tools.cnv_pipeline.steps.preprocess as step_pre

from paleomix.config import \
    ConfigError, \
    PerHostValue, \
    PerHostConfig

from paleomix.ui import \
    print_err


_DESCRIPTION = \
    "Commands:\n" \
    "  -- %prog help        -- Display this message.\n" \
    "  -- %prog preprocess  -- TODO.\n" \
    "  -- %prog run [...]   -- TODO.\n"


class CustomHelpFormatter(optparse.IndentedHelpFormatter):
    def format_description(self, description):
        return description or ""


def _run_config_parser(argv):
    per_host_cfg = PerHostConfig("phylo_pipeline")
    usage_str = "%prog <command> [options] [makefiles]"
    version_str = "%%prog v%s" % (paleomix.__version__,)
    parser = optparse.OptionParser(usage=usage_str,
                                   version=version_str)
    parser.formatter = CustomHelpFormatter()
    parser.formatter.set_parser(parser)
    parser.description = _DESCRIPTION

    paleomix.ui.add_optiongroup(parser,
                                ui_default=PerHostValue("running"),
                                color_default=PerHostValue("on"))
    paleomix.logger.add_optiongroup(parser, default=PerHostValue("warning"))

    group = optparse.OptionGroup(parser, "Scheduling")
    group.add_option("--max-threads", default=per_host_cfg.max_threads,
                     type=int,
                     help="Maximum total number of threads to use [%default]")
    group.add_option("--dry-run", default=False, action="store_true",
                     help="If passed, only a dry-run in performed, the "
                          "dependency tree is printed, and no tasks are "
                          "executed.")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Required paths")
    group.add_option("--temp-root", default=per_host_cfg.temp_root,
                     help="Location for temporary files [%default]")
    group.add_option("--destination", default="./results",
                     help="The destination for results [%default]")
    group.add_option("--mask-dir", default="./mask_dir",
                     help="The destination for results [%default]")
    parser.add_option_group(group)

    group = optparse.OptionGroup(parser, "Files and executables")
    group.add_option("--list-executables", action="store_true", default=False,
                     help="List all executables required by the pipeline, "
                          "with version requirements (if any).")
    group.add_option("--to-dot-file", dest="dot_file",
                     help="Write dependency tree to the specified dot-file.")
    parser.add_option_group(group)

    return per_host_cfg.parse_args(parser, argv)


def main(argv):
    try:
        config, args = _run_config_parser(argv)
        valid = False
        # Command, genome, makefiles
        valid |= (len(args) >= 2) and (args[0] == "preprocess")
        # Command, genome, makefiles
        valid |= (len(args) >= 2) and (args[0] == "analyse")

        if not valid:
            description = _DESCRIPTION.replace("%prog", "cnv_pipeline").strip()
            console.print_info("CNV Pipeline v%s\n" % (paleomix.__version__,))
            console.print_info(description)
            return 1

        paleomix.ui.set_ui_colors(config.ui_colors)
    except ConfigError, error:
        print_err(error)
        return 1

    if not os.path.exists(config.temp_root):
        try:
            os.makedirs(config.temp_root)
        except OSError, error:
            print_err("ERROR: Could not create temp root:\n\t%s" % (error,))
            return 1

    if not os.access(config.temp_root, os.R_OK | os.W_OK | os.X_OK):
        print_err("ERROR: Insufficient permissions for temp root: '%s'"
                  % (config.temp_root,))
        return 1

    logfile_template = time.strftime("phylo_pipeline.%Y%m%d_%H%M%S_%%02i.log")
    paleomix.logger.initialize(config, logfile_template)
    logger = logging.getLogger(__name__)

    makefiles = makefile.read_makefiles(config, args[1:])

    pipeline = paleomix.pipeline.Pypeline(config)
    if args[0] == "preprocess":
        for mkfile in makefiles:
            pipeline.add_nodes(step_pre.build_pipeline(config, mkfile))

    if config.list_executables:
        logger.info("Printing required executables ...")
        pipeline.print_required_executables()
        return 0
    elif config.dot_file:
        logger.info("Writing dependency graph to %r ...", config.dot_file)
        if not pipeline.to_dot(config.dot_file):
            return 1
        return 0

    if not pipeline.run(max_threads=config.max_threads,
                        dry_run=config.dry_run,
                        progress_ui=config.progress_ui):
        return 1
    return 0
