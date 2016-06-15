import click
from sh import git
import activegit

@click.command()
@click.argument('repopath', type=str)
@click.option('--bare', type=bool, default=True)
@click.option('--shared', type=str, default='group')
def initrepo(repopath, bare, shared):
    """ Initialize an activegit repo. 
    Default makes base shared repo that should be cloned for users """

    ag = activegit.ActiveGit(repopath, bare=bare, shared=shared)


@click.command()
@click.argument('barerepo', type=str)
@click.argument('userrepo', type=str)
def clonerepo(barerepo, userrepo):
    """ Clone a bare base repo to a user """

    git.clone(barerepo, userrepo)
    ag = activegit.ActiveGit(userrepo)
