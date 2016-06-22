from invoke import task
from jingtai import Site


site = Site('/%(project_name)s/')


@task
def serve(ctx):
    site.watch('site')
    site.watch('templates')
    site.serve(port=8000)


@task
def serve_build(ctx):
    site.serve_build(port=8000)


@task
def build(ctx):
    site.build()


@task
def clean(ctx):
    site.clean()


@task
def publish(ctx):
    site.publish()


NEW_PAGE_TEMPLATE = u"""\
title: %s

===

-inherit base.plim

#content
    Here is some content
"""


@task
def new_page(ctx, title, path):
    from jingtai.compat import Path
    new_file = Path('site') / path
    if new_file.suffix == '':
        new_file = new_file / 'index.plim'
    if not new_file.parent.exists():
        new_file.parent.mkdir(parents=True)
    with new_file.open('w') as fp:
        fp.write(NEW_PAGE_TEMPLATE % title)
