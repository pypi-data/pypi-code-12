import os
import sys

import pip


def check_settings_module_or_exit(env=None):
    try:
        env = env or os.environ['DJANGO_CONFIGURATION']
        return __import__(os.environ['DJANGO_SETTINGS_MODULE'], fromlist=[env])
    except ImportError as m:
        print('Can not load settings module. Wrong directory?')
        print('-' * 50)
        print('Error: %s' % m)
        print()

        print()

        sys.exit(1)


def load_env():
    os.environ['DJANGO_SETTINGS_MODULE'] = os.environ.get('DJANGO_SETTINGS_MODULE', 'settings')

    app_path = os.environ.get('CRATIS_APP_PATH', os.getcwd())
    sys.path += (app_path,)

    check_settings_module_or_exit()


def install_feature_dependencies(params):

    load_env()

    from django.conf import settings

    for feature in settings.APP.features:
        deps = feature.get_deps()
        if deps:
            if not params.dump:
                print('*' * 40)
                print(feature.__class__.__name__)
                print('*' * 40)

                print('Installing %s' % (', '.join(deps)))
                cmd = ('install',)
                if params.upgrade:
                    cmd += ('--upgrade',)

                non_url_deps = [dep for dep in deps if not dep.startswith('-e ')]
                url_deps = [dep for dep in deps if dep.startswith('-e ')]
                pip.main(list(cmd + tuple(non_url_deps)))

                for dep in url_deps:
                    pip.main(list(cmd + ('-e', dep[3:])))

                print('')

            else:

                print('\n#' + feature.__class__.__name__)
                for dep in deps:
                    print(dep)

    if os.path.exists('requirements.txt') and not params.dump:
        print('')
        print('*' * 40)
        print('requirements.txt')
        print('*' * 40)

        pip.main(['install', '-r', 'requirements.txt'])
