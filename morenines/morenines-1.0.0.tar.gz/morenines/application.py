import click
import os
import sys

from morenines.index import Index
from morenines.ignores import Ignores
from morenines.repository import Repository
from morenines.util import get_files, get_hash, get_new_and_missing, abort
from morenines.output import info, success, warning, error, print_filelists


pass_repository = click.make_pass_decorator(Repository, ensure=True)

DEFAULT_PATH = os.getcwd()

def repo_path_callback(ctx, param, value):
    repo = ctx.ensure_object(Repository)
    if value:
        repo.open(value)
    else:
        repo.open(DEFAULT_PATH)
    return value


_common_params = {
    'new_repo_path' : click.argument("repo_path", required=False, default=DEFAULT_PATH, type=click.Path(resolve_path=True)),
    'repo_path': click.argument("repo_path", expose_value=False, required=False, callback=repo_path_callback, type=click.Path(resolve_path=True)),
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
@common_params('new_repo_path')
@click.pass_context
def init(ctx, repo_path):
    repo = Repository()

    repo.create(repo_path)

    ctx.obj = repo

    success("Initialized empty morenines repository in {}".format(repo.mn_dir_path))


@main.command(short_help="Write a new index file")
@common_params('repo_path')
@pass_repository
def create(repo):
    """Write a new index file with the hashes of files under it."""

    if os.path.isfile(repo.index_path):
        error("Index file already exists: {}".format(repo.index_path))
        error("(To update an existing index, use the 'update' command)")
        abort()

    files, ignored = get_files(repo.path, repo.ignore)

    repo.index.add(files)

    with click.open_file(repo.index_path, mode='w') as stream:
        repo.index.write(stream)

    success('Wrote index file {}'.format(repo.index_path))


@main.command(short_help="Update an existing index file")
@common_params('repo_path')
@pass_repository
@click.option('--add-new/--no-add-new', default=False, help="Hash and add any files that aren't in the index")
@click.option('--remove-missing/--no-remove-missing', default=False, help="Delete any the hashes of any files in the index that no longer exist.")
def update(repo, add_new, remove_missing):
    """Update an existing index file with new file hashes, missing files removed, etc."""
    new_files, missing_files, ignored_files = get_new_and_missing(repo)

    if add_new:
        repo.index.add(new_files)

    if remove_missing is True:
        repo.index.remove(missing_files)

    if not any([new_files, missing_files]):
        info("Index is up-to-date (no new or missing files)")
    elif add_new or remove_missing:
        with click.open_file(repo.index_path, mode='w') as stream:
            repo.index.write(stream)
        success("Wrote index file {}".format(repo.index_path))
    else:
        warning("No action taken (use '--add-new' or '--remove-missing' to change the index)")


@main.command(short_help="Show new, missing or ignored files")
@common_params('repo_path', 'ignored', 'color')
@click.option('--verify/--no-verify', default=False, help="Re-hash all files in index and check for changes")
@pass_repository
@click.pass_context
def status(ctx, repo, show_ignored, show_color, verify):
    """Show any new files not in the index, index files that are missing, or ignored files."""
    new_files, missing_files, ignored_files = get_new_and_missing(repo, show_ignored)

    changed_files = []

    if verify:
        for path, old_hash in repo.index.files.iteritems():
            if path in missing_files:
                continue

            current_hash = get_hash(os.path.join(repo.path, path))

            if current_hash != old_hash:
                changed_files.append(path)

    ctx.color = show_color

    print_filelists(new_files, changed_files, missing_files, ignored_files)


@main.command(name='edit-ignores', short_help="Open the ignores file in an editor")
@common_params('repo_path')
@pass_repository
def edit_ignores(repo):
    """Open an existing or a new ignores file in an editor."""

    click.edit(filename=repo.ignore_path)


if __name__ == '__main__':
    main()
