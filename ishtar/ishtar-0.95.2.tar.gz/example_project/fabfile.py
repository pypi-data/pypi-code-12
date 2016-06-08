from fabric.api import env, run, cd

env.hosts = ['root@lysithea.proxience.com']

def _deploy(directory=''):
    with cd(directory):
        run('git pull')
        run('/root/bin/redmine_git_fetch')
        run('./manage.py compilemessages -l fr')
        run('/etc/init.d/apache2 restart')
        with cd('../docs'):
            run('make html')

def deploy_test():
    _deploy('/var/local/ishtar/ishtar')

def deploy_prod():
    _deploy('/var/local/ishtar-test/ishtar')
