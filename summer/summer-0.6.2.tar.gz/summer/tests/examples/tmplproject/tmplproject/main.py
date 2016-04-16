# -*- coding: utf-8 -*-
# Time-stamp: < main.py (2016-02-08 19:49) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Main entry point to the program."""

import logging

# configure logging as soon as possible
logger = logging.getLogger(__name__)

from summer import Filter
from summer.ipythonutils import run_ipshell

from .appcontext import ApplicationContext
from .manager import Category
from .cmdline import SHELL


def main(args):
    """Entry point to our program."""
    ctx = ApplicationContext(__file__, "tmplproject.cfg")
    logger.info("sample started")
    (options, args) = ctx.my_option_parser.parse_args(args)
    logger.info("args: %s", args)
    logger.info("options: %s", options)
    # create the sample database
    ctx.session_factory.create_schema()
    # do the specified action
    process_args(args, options, ctx)
    logger.info("sample finished")


def process_args(args, options, ctx):
    """Process the command line and takes the proper action."""
    if len(args) > 0:
        command = args[0]
        logger.info("running command '%s'", command)
        if command == SHELL:
            run_ipshell("Embedded IPython Shell Banner", {"ctx": ctx})
        else:
            ctx.my_option_parser.print_help()
    else:  # take the default action
        do_demonstration(ctx, options.use_ldap)


def do_demonstration(ctx, use_ldap):
    mark = "PROGRAM OUTPUT>"

    # l10n
    logger.info("%s test localization -- %s", mark, _("localized message"))

    # db
    # we need a proxied version cause we want database transactions
    logger.info("let's create some objects and persist them")
    category_dao = ctx.category_dao_proxy
    for i in range(1, 16):
        cat = Category()
        cat.order = i
        cat.code = "code_%02d" % (cat.order,)
        category_dao.save(cat)

    # we go through result set using paging
    logger.info(
        "let's iterate using db paging through what we have just persisted")
    cat_filter = Filter(1, 5)
    for page in range(1, 4):
        cat_filter.page = page
        logger.info("%s page %d", mark, cat_filter.page)
        for cat in category_dao.find(cat_filter):
            logger.info("%s %s", mark, cat)

    # ldap
    if use_ldap:
        logger.info("let's use LDAP demo query for arbitrary objects" +
                    " (not all of them, just those with ou=users)")
        user_manager = ctx.user_manager_proxy
        for user in user_manager.find():
            logger.info("%s %s", mark, user)
