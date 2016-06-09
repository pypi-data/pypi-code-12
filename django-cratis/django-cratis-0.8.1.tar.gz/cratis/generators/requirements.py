import os

from pkg_resources import Requirement


def add_to_requirements(package_name, url=None, file_path='requirements.txt'):

    if not url:
        url = package_name

    if os.path.exists(file_path):
        with open(file_path) as f:
            lines = f.read().strip().splitlines()
    else:
        lines = []

    append = True
    new_lines = []
    for line in lines:
        if line.endswith('#egg=%s' % package_name) or Requirement.parse(line).project_name == package_name:
            new_lines.append(url)
            append = False
        else:
            new_lines.append(line)

    if append:
        new_lines.append(url)

    with open(file_path, 'w') as f:
        f.write('\n'.join(new_lines))
