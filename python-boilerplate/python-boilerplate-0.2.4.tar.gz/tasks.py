from invoke import run, task

# Import some boilerplate tasks (see http://... for references)
from python_boilerplate.tasks import bump_version, build


# Add your tasks in here
# This task can be executed with ``invoke build --docs``. A better version
# of this function exists in the python_boilerplate.tasks module
@task
def build(no_docs=False):
    """Build python package and docs"""

    run("python setup.py build")
    if not no_docs:
        run("python setup.py build_sphinx")