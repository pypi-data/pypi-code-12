import sys
import shutil

from ..compat import Path


def create_project():
    if len(sys.argv) <= 1:
        print('Must provide a project name')
        return

    proj_name = sys.argv[1]
    resources = Path(__file__).parent / 'resources'

    root = Path(proj_name)
    root.mkdir()

    (root / 'tasks.py').write_text(
        (resources / 'tasks.py').read_text() % {'project_name': proj_name}
    )

    site = root / 'site'
    site.mkdir()

    shutil.copy(str(resources / '404.html'), str(site))
    shutil.copy(str(resources / 'index.plim'), str(site))

    templates = root / 'templates'
    templates.mkdir()

    shutil.copy(str(resources / 'base.plim'), str(templates))
