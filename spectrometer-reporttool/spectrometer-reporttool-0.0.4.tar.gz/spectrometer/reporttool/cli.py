# -*- coding: utf-8 -*-

# @License EPL-1.0 <http://spdx.org/licenses/EPL-1.0>
##############################################################################
# Copyright (c) 2016 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################

import click

from spectrometer.reporttool.git import GitReport


@click.group()
@click.option('--server-url', default='https://spectrometer.opendaylight.org/api/',
              help='URL to Spectrometer API server.')
@click.pass_context
def cli(ctx, server_url):
    ctx.obj['SERVER_URL'] = server_url


@click.command()
@click.argument('ref1')
@click.argument('ref2')
@click.pass_context
def full(ctx, ref1, ref2):
    git_data = GitReport(ctx.obj['SERVER_URL'], ref1, ref2)
    git_data.print_report()


cli.add_command(full)
cli(obj={})
