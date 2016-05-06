# Copyright 2016 Joseph Wright <rjosephwright@gmail.com>
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import os
import json

import click
import jinja2 as j
import yaml

import bossformation.core as bf

@click.group()
def main(): pass

@main.command()
@click.option('-t', '--template', help='Path to template file')
@click.option('-p', '--properties', help='Path to properties file')
@click.option('-P', '--pretty/--no-pretty', help='Pretty print JSON output')
def render(template, properties, pretty):
    props = bf.expand_properties(properties) if properties else {}
    if '__template__' in props:
        template = '{}.yml'.format(props['__template__'])
        loader = j.PackageLoader('bossformation', 'resources')
    else:
        loader = j.FileSystemLoader('.')

    expanded = bf.expand_template(template, props, loader)

    pargs = {'indent': 2, 'separators': (',', ': ')} if pretty else {}

    click.echo(json.dumps(expanded, **pargs))
