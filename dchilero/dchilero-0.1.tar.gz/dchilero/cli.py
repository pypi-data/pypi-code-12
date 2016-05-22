import argparse
import os


def main():  # pragma: no cover
    commands = ['create_migrate', ' create_resource', 'newproject']
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='{}'.format(commands))
    parser.add_argument('name', help='project name')
    args = parser.parse_args()

    if args.command not in commands or args is None:
        print('please add command {}'.format(commands))
    if args.command == 'create_migrate':
        create_migrate(args.name)

    if args.command == 'create_resource':
        create_migrate(args.name)
        create_resource(args.name)

    if args.command=='newproject':
        create_newproject(args.name)


def create_newproject(name):
    os.system("git clone "
              "https://keller_matta@bitbucket.org/keller_matta/newprojectchilero.git")

    for a in os.walk("."):
        if 'newprojectchilero' in a[1] or a[1] == name:
            os.renames('newprojectchilero', name)
            os.chdir(a[0]+'/{}'.format(name))

    for a in os.walk("."):

        if 'newprojectchilero' in a[1] or a[1] == name:
            os.renames('newprojectchilero', name)


def create_resource(name):
    resources = get_path('resources')
    if resources:
        path = resources[0] + '/resources'
        os.chdir(path)
        os.system('touch {}.py'.format(name))
        os.system('git add .')


def create_migrate(name):
    count = 1
    migrations = get_path('migrations')
    if migrations:
        path = migrations[0] + '/migrations'
        for o in os.listdir(path):
            count += 1
        count = str(count).zfill(3)
        name = '{}-{}'.format(count, name)
        path += '/{}'.format(name)
        os.mkdir(path)
        os.system('touch {}/forward.sql {}/backward.sql'.format(path, path))
        os.system('git add .')
        print('migrations created')
    else:
        print('not exist migrations directory')


def get_path(search):
    for a in os.walk("."):
        if search in a[1]:
            return a


if __name__ == '__main__':  # pragma: no cover
    main()