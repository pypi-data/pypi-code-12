# -*- coding: utf-8 -*-

import click
from . import utils, branches
import os


@click.group()
def cli():
    pass


@cli.command()
@click.option("-f", "--json-file", help="Json file to use", required=True)
@click.option("-p", "--path",
              help="Path of GIT Repo, actual dir by default. May be a list for save option",
              default=None)
@click.option("--recursive/--no-recursive", default=True,
              help="Sets the search of repositories as recursive or no recursive. Recursive by default")
def save(json_file, path, recursive):
    """save command
    """
    if not path:
        path = os.getcwd()
    path_list = path.split(',')
    gitbranch = branches.GitBranch()
    for path in path_list:
        b_info = gitbranch.get_branches(path, recursive=recursive)
        b_info_simple = utils.simplify_path(b_info)
        utils.save_json(b_info_simple, json_file)


@cli.command()
@click.option("-f", "--json-file", help="Json file to use", required=True)
@click.option("-p", "--path",
              help="Path of GIT Repo, actual dir by default. May be a list for save option",
              default=None)
@click.option("--tmp", help="Temporary directory for branches files",
              default="/tmp")
def load(json_file, path, tmp):
    if not path:
        path = os.getcwd()
    path_list = path.split(',')
    gitbranch = branches.GitBranch()
    b_info_file = utils.load_json(json_file)
    for path in path_list:
        branches.action_file(tmp, "pre_process.json", path)
        for branch in b_info_file:
            gitbranch.set_branch(branch, path)
        branches.action_file(tmp, "post_process.json", path)


@cli.command()
@click.option("-p", "--path",
              help="Path of GIT Repo, actual dir by default. May be a list for save option",
              default=None)
@click.option("--tmp", help="Temporary directory for branches files",
              default="/tmp")
@click.option("-R", "--recursive",
              help="Sets the seek of repositories as recursive. False by default",
              is_flag=True, default=False)
def pull(path, tmp, recursive):
    if not path:
        path = os.getcwd()
    path_list = path.split(',')
    gitbranch = branches.GitBranch()
    for path in path_list:
        b_info = gitbranch.get_branches(path, recursive=recursive)
        b_info_simple = utils.simplify_path(b_info)
        branches.action_file(tmp, "pre_process.json", path)
        for branch in b_info_simple:
            gitbranch.pull(branch, path)
        branches.action_file(tmp, "post_process.json", path)
