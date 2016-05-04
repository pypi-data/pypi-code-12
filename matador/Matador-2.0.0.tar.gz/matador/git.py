import logging
from dulwich.client import LocalGitClient
from dulwich.index import build_index_from_tree
from dulwich.objects import Tag, format_timezone
from time import strftime, gmtime
import re

logger = logging.getLogger(__name__)


def stage_file(repo, file):
    """Stage a file to the index

    The equivalent of :code:`git add`

    Parameters
    ----------
    repo : dulwich.repo.Repo
    file : pathlib.Path
    """
    file_path = str(file.relative_to(repo.path))
    repo.stage(file_path)


def commit(repo, message):
    """Commit the index to the repository

    The equivalent of :code:`git commit`

    Parameters
    ----------
    repo : dulwich.repo.Repo
    message : str
    """
    message = bytes(message, encoding='UTF-8')
    repo.do_commit(message)


def fetch_all(source_repo, target_repo, remote_name=None):
    """Fetch branches and tags from a remote repository

    Unlike :code:`git fetch`, this will also update local branches to point at
    the same commit as their remote counterpart.

     Parameters
    ----------
    source_repo : dulwich.repo.Repo
    target_repo : dulwich.repo.Repo
    remote_name : str
    """
    if remote_name is None:
        remote_name = 'origin'

    refs = LocalGitClient().fetch(source_repo.path, target_repo)

    for key, value in refs.items():
        remote_key = key.replace(
            b'heads', b'remotes/%s' % bytes(remote_name, encoding='UTF-8'))
        target_repo.refs[remote_key] = value
        target_repo[key] = value


def full_ref(repo, ref):
    """Generate a fully qualified git reference

    If ref refers to a branch or tag, the function will return the correct
    fully qualified reference, otherwise it returns the ref as provided.

    e.g. for ref 'master', return 'refs/heads/master'

    Parameters
    ----------
    repo : dulwich.repo.Repo

    Returns
    -------
    str
    """
    refs = repo.refs.keys()
    for ref_type in ['refs/heads/', 'refs/tags/']:
        full_ref = ref_type + ref
        if bytes(full_ref, encoding='ascii') in refs:
            ref = full_ref
    return ref


def checkout(repo, ref=None):
    """Checkout the commit from a given ref to the working directory

    The equivalent of :code:`git checkout`

    Parameters
    ----------
    repo : dulwich.repo.Repo
    ref : str

    Returns
    -------
    list
    """
    if ref is None:
        ref = repo.head()
    else:
        ref = bytes(full_ref(repo, ref), encoding='ascii')

    if isinstance(repo[ref], Tag):
        sha = repo[ref].object[1]
        tree_id = repo[sha].tree
    else:
        tree_id = repo[ref].tree

    index = repo.index_path()
    build_index_from_tree(repo.path, index, repo.object_store, tree_id)
    return [repo.object_store.iter_tree_contents(tree_id)]


def keyword_values(repo, ref):
    expanded_ref = bytes(full_ref(repo, ref), encoding='ascii')
    version = None
    commit_timestamp = None
    author = None

    try:
        if isinstance(repo[expanded_ref], Tag):
            sha = repo[expanded_ref].object[1]
        else:
            sha = repo.refs[expanded_ref]

        short_sha = sha[:7].decode(encoding='ascii')
        commit = repo.get_object(sha)
        commit_time = strftime('%Y-%m-%d %H:%M:%S', gmtime(commit.commit_time))
        timezone = format_timezone(
            commit.commit_timezone).decode(encoding='ascii')
        commit_timestamp = commit_time + ' ' + timezone
        author = commit.author.decode(encoding='ascii')

        if ref.startswith('refs/tags'):
            version = 'Tag %s (%s)' % (ref, short_sha)
        else:
            version = short_sha

    except KeyError:
        logger.error('%s is not a valid branch or tag' % ref)

    return version, commit_timestamp, author


def substitute_keywords(text, repo, ref):
    """Perform keyword substitution on given text

    Substitutes the keywords 'version:', 'date:' and 'author:' with the
    relevant attributes extracted from the repository for the given ref.

    Parameters
    ----------
    text : str
    repo : dulwich.repo.Repo
    ref : str

    Returns
    -------
    str
    """
    new_text = ''
    version, commit_timestamp, author = keyword_values(repo, ref)

    if version is not None:

        substitutions = {
            'version': version,
            'date': commit_timestamp,
            'author': author
        }

        for line in text.splitlines(keepends=True):
            for key, value in substitutions.items():
                rexp = '%s:.*' % key
                line = re.sub(rexp, '%s: %s' % (key, value), line)
            new_text += line

    return new_text
