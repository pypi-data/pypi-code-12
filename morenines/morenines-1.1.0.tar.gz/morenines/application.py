import click
import os
import sys

from morenines.index import Index
from morenines.ignores import Ignores
from morenines.repository import Repository
from morenines.util import get_files, get_hash, get_new_and_missing, abort
from morenines.output import info, success, warning, error, print_filelists
from morenines.exceptions import PathError, NoEffectWarning


pass_repository = click.make_pass_decorator(Repository, ensure=True)

def default_repo_path():
    return os.getcwd()

_common_params = {
    'ignored': click.option('-i', '--ignored/--no-ignored', 'show_ignored', default=False, help="Enable/disable showing files ignored by the ignores patterns."),
    'color': click.option('--color/--no-color', 'show_color', default=True, help="Enable/disable colorized output."),
}

def common_params(*param_names):
    def real_decorator(func):
        for param_name in param_names:
            func = _common_params[param_name](func)
        return func

    return real_decorator


@click.group()
def main():
    """A tool to track whether the content of files has changed."""
    pass


@main.command(short_help="Initialize a new morenines repository")
@click.argument("repo_path", required=False, type=click.Path(resolve_path=True))
@pass_repository
def init(repo, repo_path):
    """Create the morenines repository (the .morenines directory and associated
       files) in REPO_PATH, the parent directory containing all files (including
       in subdirs) that will be tracked.

    Must not be called inside an existing repository.
    """
    if not repo_path:
        repo_path = default_repo_path()

    try:
        repo.create(repo_path)
    except PathError as e:
        error(e)
        abort()

    success("Initialized empty morenines repository in {}".format(repo.mn_dir_path))


@main.command(short_help="Hash and add any files that aren't in the index")
@pass_repository
@click.argument("paths", required=False, nargs=-1, type=click.Path(resolve_path=True))
def add(repo, paths):
    """Update an existing index wtih new file hashes.

    Must be called from inside an existing repository.
    """
    try:
        repo.open(default_repo_path())
    except PathError as e:
        error(e)
        abort()

    if not paths:
        warning("No action taken (supply one or more PATHS to files to add to the repository)")
        return

    try:
        added_paths = repo.add(paths)
    except NoEffectWarning as w:
        warning(w)
        return
    except PathError as e:
        error(e)
        abort()

    try:
        repo.write_index()
    except RepositoryError as e:
        error(e)
        abort()

    success("Files added to repository:", added_paths)


@main.command(short_help="Remove the hashes of supplied paths from the index.")
@pass_repository
@click.argument("paths", required=False, nargs=-1, type=click.Path(resolve_path=True))
def remove(repo, paths):
    """Update the repository to remove paths from it.

    Must be run while inside a repository.
    """
    try:
        repo.open(default_repo_path())
    except PathError as e:
        error(e)
        abort()

    if not paths:
        warning("No action taken (supply one or more PATHS to files to add to the repository)")
        return

    try:
        removed_paths = repo.remove(paths)
    except NoEffectWarning as w:
        warning(w)
        return
    except PathError as e:
        error(e)
        abort()

    try:
        repo.write_index()
    except RepositoryError as e:
        error(e)
        abort()

    success("Files removed from repository:", removed_paths)


@main.command(short_help="Show new, missing or ignored files")
@common_params('ignored', 'color')
@click.option('--verify/--no-verify', default=False, help="Re-hash all files in index and check for changes")
@pass_repository
@click.pass_context
def status(ctx, repo, show_ignored, show_color, verify):
    """Show any new files not in the index, index files that are missing, or ignored files.

    Must be called from inside an existing repository.
    """
    try:
        repo.open(default_repo_path())
    except PathError as e:
        error(e)
        abort()

    new_files, missing_files, ignored_files = get_new_and_missing(repo, show_ignored)

    changed_files = []

    if verify:
        for path, old_hash in repo.index.files.items():
            if path in missing_files:
                continue

            current_hash = get_hash(os.path.join(repo.path, path))

            if current_hash != old_hash:
                changed_files.append(path)

    ctx.color = show_color

    print_filelists(new_files, changed_files, missing_files, ignored_files)


@main.command(name='edit-ignores', short_help="Open the ignores file in an editor")
@pass_repository
def edit_ignores(repo):
    """Open an existing or a new ignores file in an editor.

    Must be called from inside an existing repository.
    """
    try:
        repo.open(default_repo_path())
    except PathError as e:
        error(e)
        abort()

    click.edit(filename=repo.ignore_path)


@main.command(name='help', short_help="Display help text")
@click.argument('command', required=False)
def help(command):
    """Display help text, optionally for the given command"""
    if command:
        main([command, '--help'])
    else:
        main(['--help'])


if __name__ == '__main__':
    main()
