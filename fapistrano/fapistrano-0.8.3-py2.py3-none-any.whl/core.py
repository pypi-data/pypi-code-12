# -*- coding: utf-8 -*-

def start_deploy():
    _start_deploy()

def start_rollback():
    env.rollback_from = get_current_release()
    env.rollback_to = get_previous_release()
    env.release_path = '%(releases_path)s/%(rollback_to)s' % env
    _check_rollback_to()

def update_deploy():
    pass

def revert_deploy():
    pass

def publish_deploy():
    _symlink_current()

def finish_rollback_deploy():
    _cleanup_rollback()

def finish_deploy():
    _cleanup()

def _start_deploy():
    _check()
    _symlink_shared_files()

def _check():
    run('mkdir -p %(path)s/{releases,shared/log}' % env)
    run('chmod -R g+w %(shared_path)s' % env)
    run('mkdir -p %(release_path)s' % env)
    for linked_file_dir in get_linked_file_dirs():
        dir = '%(release_path)s/' % env
        dir += linked_file_dir
        run('mkdir -p %s' % dir)
    for linked_dir_parent in get_linked_dir_parents():
        dir = '%(release_path)s/' % env
        dir += linked_dir_parent
        run('mkdir -p %s' % dir)

def _symlink_shared_files():
    for linked_file in get_linked_files():
        env.linked_file = linked_file
        if exists('%(release_path)s/%(linked_file)s' % env):
            run('rm %(release_path)s/%(linked_file)s' % env)
        run('ln -nfs %(shared_path)s/%(linked_file)s %(release_path)s/%(linked_file)s' % env)
    for linked_dir in get_linked_dirs():
        env.linked_dir = linked_dir
        if exists('%(release_path)s/%(linked_dir)s' % env):
            run('rm -rf %(release_path)s/%(linked_dir)s' % env)
        run('ln -nfs  %(shared_path)s/%(linked_dir)s %(release_path)s/%(linked_dir)s' % env)


def _symlink_current():
    run('ln -nfs %(release_path)s %(current_path)s' % env)

def _check_rollback_to():
    if not env.release_path:
        abort('No release to rollback')

def _cleanup_rollback():
    run('rm -rf %(releases_path)s/%(rollback_from)s' % env)

def _cleanup():
    with cd(env.releases_path):
        outdated_releases = get_outdated_releases()
        if outdated_releases:
            run('rm -rf %s' % ' '.join(outdated_releases))
