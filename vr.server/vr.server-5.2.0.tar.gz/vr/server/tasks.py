import contextlib
import datetime
import functools
import logging
import os.path
import traceback
import time
import json

from collections import defaultdict

import six
from six.moves import range

import yaml
import fabric.network
import fabric.state
import redis
from celery.task import subtask, chord, task
from fabric.context_managers import settings as fab_settings
from django.conf import settings
from django.utils import timezone
from django.core.files import File
from django.core.files.base import ContentFile

from vr.builder.main import BuildData
from vr.imager.command import ImageData
from vr.common import utils
from vr.common.models import Proc
from vr.common.utils import tmpdir
from vr.server.utils import build_swarm_trace_id
from vr.server import events, balancer, remote
from vr.server.models import (Release, Build, Swarm, Host, PortLock, TestRun,
                              TestResult, BuildPack, OSImage)

MAX_EVENT_MESSAGE_LEN = 10000
PORTLOCK_MAX_AGE_DAYS = 7

logger = logging.getLogger('velociraptor.tasks')


def send_event(title, msg, tags=None, **kw):
    logger.info(msg)
    # Create and discard connections when needed.  More robust than trying to
    # hold them open for a long time.
    sender = events.EventSender(
        settings.EVENTS_PUBSUB_URL,
        settings.EVENTS_PUBSUB_CHANNEL,
        settings.EVENTS_BUFFER_KEY,
        settings.EVENTS_BUFFER_LENGTH,
    )

    def _trim(msg):
        if not isinstance(msg, six.string_types):
            return msg
        if len(msg) < MAX_EVENT_MESSAGE_LEN:
            return msg

        n = int(MAX_EVENT_MESSAGE_LEN / 2)
        sep = '\n\n...<snip>...\n\n'
        return msg[:n] + sep + msg[-n:]

    sender.publish(_trim(msg), title=title, tags=tags, **kw)
    sender.close()


def send_debug_event(title, msg=''):
    if settings.DEBUG:
        send_event(title, msg, tags=['debug'])


class event_on_exception(object):
    """
    Decorator that puts a message on the pubsub for any exception raised in the
    decorated function.
    """

    def __init__(self, tags=None):
        self.tags = tags or []
        self.tags.append('failed')

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)

            except remote.Error as e:
                logger.warning('Notifying remote error: %r', e)
                swarm_trace_id = kwargs.get('swarm_trace_id')

                try:
                    send_event(title=e.title, msg=e.out,
                               tags=self.tags, swarm_trace_id=swarm_trace_id)
                except:
                    pass

                # Re-raise exception
                raise e

            except (Exception, SystemExit) as e:
                logger.warning('Notifying error: %r', e)
                swarm_trace_id = kwargs.get('swarm_trace_id')

                try:
                    send_event(title=str(e), msg=traceback.format_exc(),
                               tags=self.tags, swarm_trace_id=swarm_trace_id)
                except:
                    pass

                # Re-raise exception
                raise e

        return wrapper


def build_proc_info(release, config_name, hostname, proc, port):
    """
    Return a dictionary with exhaustive metadata about a proc.  This is saved
    as the proc.yaml file that is given to the runner.
    """

    build = release.build
    app = build.app
    proc_info = {
        'release_hash': release.hash,
        'config_name': config_name,
        'settings': release.config_yaml or {},
        'env': release.env_yaml or {},
        'version': build.tag,
        'build_md5': build.file_md5,
        'build_url': build.file.url,
        'buildpack_url': build.buildpack_url,
        'buildpack_version': build.buildpack_version,
        'app_name': app.name,
        'app_repo_url': app.repo_url,
        'app_repo_type': app.repo_type,
        'host': hostname,
        'proc_name': proc,
        'port': port,
        'user': release.run_as or 'nobody',
        'group': 'nogroup',
        'volumes': release.volumes or [],
        'mem_limit': release.mem_limit,
        'memsw_limit': release.memsw_limit,
    }

    if build.os_image is not None:
        proc_info.update({
            'image_name': build.os_image.name,
            'image_url': build.os_image.file.url,
            'image_md5': build.os_image.file_md5,
        })

    return proc_info


@task
@event_on_exception(['deploy'])
def deploy(release_id, config_name, hostname, proc, port, swarm_trace_id=None):
    with unlock_port_ctx(hostname, port):
        release = Release.objects.get(id=release_id)
        logger.info(
            '[%s] Deploy %s-%s-%s to %s',
            swarm_trace_id, release, proc, port, hostname)

        msg_title = '%s-%s-%s' % (
            release.build.app.name, release.build.tag, proc)
        msg = 'deploying %s-%s-%s to %s' % (release, proc, port, hostname)
        send_event(title=msg_title, msg=msg, tags=['deploy'],
                   swarm_id=swarm_trace_id)

        assert release.build.file, "Build %s has no file" % release.build
        assert release.hash, "Release %s has not been hashed" % release

        with tmpdir():

            # write the proc.yaml locally
            with open('proc.yaml', 'wb') as f:
                info = build_proc_info(
                    release, config_name, hostname, proc, port)
                f.write(yaml.safe_dump(info, default_flow_style=False))

            with remote_settings(hostname):
                with always_disconnect(hostname):
                    remote.deploy_proc('proc.yaml')


@task
@event_on_exception(['build'])
def build_app(build_id, callback=None, swarm_trace_id=None):
    logger.info("[%s] Build %s start", swarm_trace_id, build_id)
    build = Build.objects.get(id=build_id)
    build.start()
    build.save()

    build_yaml = BuildData(get_build_parameters(build)).as_yaml()
    build_msg = "Started build %s" % build + '\n\n' + build_yaml
    send_event(str(build), build_msg, tags=['build'],
               swarm_id=swarm_trace_id)

    _do_build(build, build_yaml)

    # start callback if there is one.
    if callback is not None:
        subtask(callback).delay()

    # If there were any other swarms waiting on this build, kick them off
    build_start_waiting_swarms(build.id)


@task
@event_on_exception(['image'])
def build_image(image_id, callback=None):
    logger.info("Build image %s start", image_id)
    image = OSImage.objects.get(id=image_id)
    image_yaml = ImageData({
        'base_image_url': image.base_image_url,
        'base_image_name': image.base_image_name,
        'new_image_name': image.name,
        'script_url': image.provisioning_script_url,
    }).as_yaml()
    img_msg = "Started image build %s" % image + '\n\n' + image_yaml
    send_event(str(image), img_msg, tags=['buildimage'])

    t0 = time.time()
    with tmpdir():
        try:
            with open('image.yaml', 'wb') as f:
                f.write(image_yaml)

            with remote_settings('localhost'):
                remote.build_image('image.yaml')

            # We should now have <image_name>.tar.gz and <image_name>.log
            # locally.
            img_file = image.name + '.tar.gz'
            img_storage_path = 'images/' + img_file
            with open(img_file, 'rb') as localfile:
                image.file.save(img_storage_path, File(localfile))

            image.active = True
        finally:
            logfile = image.name + '.log'
            try:
                # grab and store the compile log.
                with open(logfile, 'rb') as f:
                    logname = 'images/' + logfile
                    image.build_log.save(logname, File(f))
            except:
                logger.info('Could not retrieve ' + logfile)
                raise
            finally:
                image.save()

    elapsed_time = time.time() - t0
    send_event(
        str(image), "Completed image %s in %d seconds" % (image, elapsed_time),
        tags=['buildimage', 'success'])

    # start callback if there is one.
    if callback is not None:
        subtask(callback).delay()


def _do_build(build, build_yaml):
    t0 = time.time()
    # enter a temp folder
    with tmpdir():
        try:
            with open('build_job.yaml', 'wb') as f:
                f.write(build_yaml)

            with remote_settings('localhost'):
                remote.build_app('build_job.yaml')

            # store the build file and metadata in the database.  There should
            # now be a build.tar.gz and build_result.yaml in the current folder
            with open('build_result.yaml', 'rb') as f:
                build_result = BuildData(yaml.safe_load(f))

            build_name = '-'.join([
                build_result.app_name,
                build_result.version,
                build_result.build_md5
            ])
            filepath = 'builds/' + build_name + '.tar.gz'
            logger.info('Saving tarball')
            with open('build.tar.gz', 'rb') as localfile:
                build.file.save(filepath, File(localfile))

            logger.info('Saving build metadata')
            build.file_md5 = build_result.build_md5
            build.env_yaml = build_result.release_data.get('config_vars', {})
            build.buildpack_url = build_result.buildpack_url
            build.buildpack_version = build_result.buildpack_version
            build.status = 'success'
            try_get_compile_log(build)

        except:
            logger.exception('Build failed')
            build.status = 'failed'
            # Don't raise, or we'll mask the real error
            try_get_compile_log(build, on_exc='pass')
            raise

        finally:
            build.end_time = timezone.now()
            build.save()

    elapsed_time = time.time() - t0
    msg = "Completed build %s in %d seconds" % (build, elapsed_time)
    send_event(str(build), msg, tags=['build', 'success'])


def try_get_compile_log(build, on_exc='raise'):
    '''
    Try to get the compile.log for the build and save it.
    '''
    try:
        # grab and store the compile log.
        with open('compile.log', 'rb') as f:
            logname = 'builds/build_%s_compile.log' % build.id
            logger.info("logname: " + logname)
            compile_contents = f.read()

            # Append the contents of lxcdebug.log if it's present.
            if os.path.isfile('lxcdebug.log'):
                with open('lxcdebug.log', 'rb') as fl:
                    lxc_contents = fl.read()
                compile_contents = '\n'.join([
                    compile_contents, '',
                    '--- LXC DEBUG LOGS FOLLOW ---', '',
                    lxc_contents
                ])
            build.compile_log.save(logname, ContentFile(compile_contents))
    except Exception as exc:
        logger.error(
            'Could not retrieve compile.log for %s: %r', build, exc)
        exec(on_exc)


def get_build_parameters(build):
    """Return a dictionary of Heroku-style build parameters."""
    app = build.app
    os_image = build.os_image

    build_params = {
        'app_name': app.name,
        'app_repo_url': app.repo_url,
        'app_repo_type': app.repo_type,
        'version': build.tag,
    }

    if os_image is not None:
        build_params.update({
            'image_name': os_image.name,
            'image_url': os_image.file.url,
            'image_md5': os_image.file_md5,
        })

    if app.buildpack:
        build_params['buildpack_url'] = app.buildpack.repo_url
    else:
        buildpacks = BuildPack.objects.order_by('order')
        urls = [bp.repo_url for bp in buildpacks]
        build_params['buildpack_urls'] = urls

    return build_params


@task(soft_time_limit=60)
@event_on_exception(['proc', 'deleted'])
def delete_proc(host, proc, callback=None, swarm_trace_id=None, retry=0):
    logger.info("[%s] Delete proc %s on host %s", swarm_trace_id, proc, host)

    # We want to retry this task a few times before giving up, but we
    # want to carry on with the swarm on failure, too.
    # Celery retry() method seems to re-raise the original exception,
    # which stops the whole swarm.
    MAX_RETRIES = 3
    RETRY_TIMEOUT = 60

    try:
        with remote_settings(host):
            with always_disconnect(host):
                remote.delete_proc(host, proc)

        send_event(Proc.name_to_shortname(proc),
                   'deleted %s on %s' % (proc, host),
                   tags=['proc', 'deleted'],
                   swarm_id=swarm_trace_id)

    except Exception as exc:
        logger.warning(
            '[%s] Error while deleting proc %s on %s: %r',
            swarm_trace_id, proc, host, exc)

        if retry >= MAX_RETRIES:
            raise

        send_event(Proc.name_to_shortname(proc),
                   'Error while deleting %s on %s: %r. Will retry.' % (
                       proc, host, exc),
                   tags=['proc', 'deleted', 'failed'],
                   swarm_id=swarm_trace_id)

        logger.warning('delete_proc: Retrying #%d', retry)
        delete_proc.apply_async(
            kwargs={
                'host': host,
                'proc': proc,
                'callback': callback,
                'swarm_trace_id': swarm_trace_id,
                'retry': retry + 1,
            }, countdown=RETRY_TIMEOUT)

    if callback is not None:
        logger.info(
            "[%s] Delete proc calling subtask %s", swarm_trace_id, callback)
        subtask(callback).delay()


def create_wait_value(swarm_id, swarm_trace_id=None):
    swarm_trace_id = swarm_trace_id or ''
    return json.dumps({'swarm_id': swarm_id,
                       'swarm_trace_id': swarm_trace_id})


def read_wait_value(key):
    # If we can't parse assume the key is the swarm_id
    doc = {'swarm_id': key, 'swarm_trace_id': None}
    try:
        doc = json.loads(key)
    except:
        pass

    return doc['swarm_id'], doc['swarm_trace_id']


def swarm_wait_for_build(swarm, build, swarm_trace_id=None):
    """
    Given a swarm that you want to have swarmed ASAP, and a build that the
    swarm is waiting to finish, push the swarm's ID onto the build's waiting
    list.
    """
    logger.info(
        "[%s] Swarm %s waiting for build %s",
        swarm_trace_id, swarm.id, build.id)
    msg = 'Swarm %s waiting for completion of build %s' % (swarm, build)
    send_event(
        '%s waiting' % swarm, msg, ['wait'], swarm_trace_id=swarm_trace_id)
    with tmpredis() as r:
        key = getattr(
            settings, 'BUILD_WAIT_PREFIX', 'buildwait_') + str(build.id)
        r.lpush(key, create_wait_value(swarm.id, swarm_trace_id))
        r.expire(key, getattr(settings, 'BUILD_WAIT_AGE', 3600))


def build_start_waiting_swarms(build_id):
    """
    Check Redis for the list of swarms waiting on a particular build.  Pop each
    off the list and call swarm_start for it.
    """
    with tmpredis() as r:
        key = getattr(
            settings, 'BUILD_WAIT_PREFIX', 'buildwait_') + str(build_id)
        swarm_id, swarm_trace_id = read_wait_value(r.lpop(key))
        while swarm_id:
            swarm_start.delay(swarm_id, swarm_trace_id)
            swarm_id = r.lpop(key)


@task
@event_on_exception(['swarm'])
def swarm_start(swarm_id, swarm_trace_id=None):
    """
    Given a swarm_id, kick off the chain of tasks necessary to get this swarm
    deployed.
    """
    logger.info("[%s] Swarm %s start", swarm_trace_id, swarm_id)
    try:
        swarm = Swarm.objects.get(id=swarm_id)
    except Swarm.DoesNotExist:
        # For some STRANGE reason, sometimes the Swarm.objects.get above will
        # raise an error saying the swarm doesn't exist, even though querying
        # it here will show that it does.  This sucks, but we can catch such
        # things sometimes.
        swarms = Swarm.objects.all()
        ids = [str(s.id) for s in swarms]
        if swarm_id in ids:
            swarm = next(s for s in swarms if s.id == swarm_id)
        else:
            raise
    build = swarm.release.build

    if not swarm_trace_id:
        swarm_trace_id = build_swarm_trace_id(swarm)

    if build.is_usable():
        # Build is good.  Do a release.
        swarm_release.delay(swarm_id, swarm_trace_id)
    elif build.in_progress():
        # Another swarm call already started a build for this app/tag.  Instead
        # of starting a duplicate, just push the swarm ID onto the build's
        # waiting list.
        swarm_wait_for_build(swarm, build, swarm_trace_id)
    else:
        # Build hasn't been kicked off yet.  Do that now.
        callback = swarm_release.subtask((swarm.id, swarm_trace_id))
        build_app.delay(build.id, callback, swarm_trace_id)


# This task should only be used as a callback after swarm_start
@task
@event_on_exception(['swarm'])
def swarm_release(swarm_id, swarm_trace_id=None):
    """
    Assuming the swarm's build is complete, this task will ensure there's a
    release with that build + current config, and call subtasks to make sure
    there are enough deployments.
    """
    logger.info("[%s] Swarm %s release", swarm_trace_id, swarm_id)
    swarm = Swarm.objects.get(id=swarm_id)
    send_debug_event('Swarm %s release' % swarm)
    build = swarm.release.build

    # Bail out if the build doesn't have a file
    assert build.file, "Build %s has no file" % build

    # swarm.get_current_release(tag) will check whether there's a release with
    # the right build and config, and create one if not.
    swarm.release = swarm.get_current_release(build.tag)
    swarm.save()

    # Ensure that the release is hashed.
    release = swarm.release
    release.save()

    # OK we have a release.  Next: see if we need to do a deployment.
    # Query squad for list of procs.
    all_procs = swarm.get_procs()
    current_procs = [p for p in all_procs if p.hash == swarm.release.hash]

    procs_needed = swarm.size - len(current_procs)

    if procs_needed > 0:
        hosts = swarm.get_prioritized_hosts()
        hostcount = len(hosts)

        # Build up a dictionary where the keys are hostnames, and the
        # values are lists of ports.
        new_procs_by_host = defaultdict(list)
        for x in range(procs_needed):
            host = hosts[x % hostcount]
            port = host.get_free_port()
            new_procs_by_host[host.name].append(port)

            # Ports need to be locked here in the synchronous loop, before
            # fanning out the async subtasks, in order to prevent collisions.
            lock_port(host, port)

        # Now loop over the hosts and fan out a task to each that needs it.
        subtasks = []
        for host in hosts:
            if host.name in new_procs_by_host:
                subtasks.append(
                    swarm_deploy_to_host.subtask((
                        swarm.id,
                        host.id,
                        new_procs_by_host[host.name],
                        swarm_trace_id
                    ))
                )
        callback = swarm_post_deploy.subtask((swarm.id, swarm_trace_id))
        chord(subtasks)(callback)
    elif procs_needed < 0:
        # We need to delete some procs

        # reverse prioritized list so the most loaded hosts get things removed
        # first.
        hosts = swarm.get_prioritized_hosts()
        hosts.reverse()
        hostcount = len(hosts)
        subtasks = []
        for x in range(procs_needed * -1):
            host = hosts[x % hostcount]
            proc = host.swarm_procs.pop()
            subtasks.append(
                swarm_delete_proc.subtask(
                    (swarm.id, host.name, proc.name, proc.port),
                    {'swarm_trace_id': swarm_trace_id}
                )

            )
        callback = swarm_post_deploy.subtask((swarm.id, swarm_trace_id))
        chord(subtasks)(callback)
    else:
        # We have just the right number of procs.  Uptest and route them.
        swarm_assign_uptests(swarm.id, swarm_trace_id)


@task
def swarm_deploy_to_host(swarm_id, host_id, ports, swarm_trace_id=None):
    """
    Given a swarm, a host, and a list of ports, deploy the swarm's current
    release to the host, one instance for each port.
    """
    # This function allows a swarm's deployments to be parallel across
    # different hosts, but synchronous on a per-host basis, which solves the
    # problem of two deployments both trying to copy the release over at the
    # same time.

    swarm = Swarm.objects.get(id=swarm_id)
    host = Host.objects.get(id=host_id)
    logger.info(
        "[%s] Swarm %s deploy to host %s",
        swarm_trace_id, swarm_id, host.name)
    for port in ports:
        deploy(
            swarm.release.id,
            swarm.config_name,
            host.name,
            swarm.proc_name,
            port,
            swarm_trace_id,
        )

    procnames = ["%s-%s-%s" % (swarm.release, swarm.proc_name, port) for port
                 in ports]

    return host.name, procnames


@task
def swarm_post_deploy(deploy_results, swarm_id, swarm_trace_id):
    """
    Chord callback run after deployments.  Should check for exceptions, then
    launch uptests.
    """
    if any(isinstance(r, Exception) for r in deploy_results):
        swarm = Swarm.objects.get(id=swarm_id)
        msg = "Error in deployments for swarm %s" % swarm
        send_event('Swarm %s aborted' % swarm, msg,
                   tags=['failed'], swarm_id=swarm_trace_id)
        raise Exception(msg)

    swarm_assign_uptests(swarm_id, swarm_trace_id)


@task
def swarm_assign_uptests(swarm_id, swarm_trace_id=None):
    logger.info("[%s] Swarm %s uptests", swarm_trace_id, swarm_id)

    swarm = Swarm.objects.get(id=swarm_id)
    all_procs = swarm.get_procs()
    current_procs = [p for p in all_procs if p.hash == swarm.release.hash]

    # Organize procs by host
    host_procs = defaultdict(list)
    for proc in current_procs:
        host_procs[proc.host.name].append(proc.name)

    header = [uptest_host_procs.subtask((h, ps)) for h, ps in
              host_procs.items()]

    if len(header):
        this_chord = chord(header)
        callback = swarm_post_uptest.s(swarm_id, swarm_trace_id)
        this_chord(callback)
    else:
        # There are no procs, so there are no uptests to run.  Call
        # swarm_post_uptest with an empty list of uptest results.
        swarm_post_uptest([], swarm_id, swarm_trace_id)


@task
def uptest_host_procs(hostname, procs):
    with remote_settings(hostname):
        with always_disconnect(hostname):
            results = {
                p: remote.run_uptests(hostname, p, settings.PROC_USER)
                for p in procs
            }
    return hostname, results


@task
def uptest_host(hostname, test_run_id=None):
    """
    Given a hostname, look up all its procs and then run uptests on them.
    """

    print('Uptest host {} run_id={}'.format(hostname, test_run_id))
    host = Host.objects.get(name=hostname)
    procs = host.get_procs()
    _, results = uptest_host_procs(hostname, [p.name for p in procs])

    if test_run_id:
        run = TestRun.objects.get(id=test_run_id)
        for procname, resultlist in results.items():
            testcount = len(resultlist)
            if testcount:
                passed = all(r['Passed'] for r in resultlist)
            else:
                # There were no tests :(
                passed = True

            tr = TestResult(
                run=run,
                time=timezone.now(),
                hostname=hostname,
                procname=procname,
                passed=passed,
                testcount=testcount,
                results=yaml.safe_dump(resultlist)
            )
            tr.save()
    return hostname, results


class FailedUptest(Exception):
    pass


@task
def swarm_post_uptest(uptest_results, swarm_id, swarm_trace_id):
    """
    Chord callback that runs after uptests have completed.  Checks that they
    were successful, and then calls routing function.
    """
    logger.info("[%s] Swarm %s post uptests", swarm_trace_id, swarm_id)

    # uptest_results will be a list of tuples in form (host, results), where
    # 'results' is a list of dictionaries, one for each test script.

    swarm = Swarm.objects.get(id=swarm_id)
    test_counter = 0
    for host_results in uptest_results:
        if isinstance(host_results, Exception):
            raise host_results
        _host, proc_results = host_results

        # results is now a dict
        for proc, results in proc_results.items():
            for result in results:
                test_counter += 1
                # This checking/formatting relies on each uptest result being a
                # dict with 'Passed', 'Name', and 'Output' keys.
                if result['Passed'] is not True:
                    msg = (proc + ": {Name} failed:"
                           "{Output}".format(**result))
                    send_event(str(swarm), msg,
                               tags=['failed', 'uptest'],
                               swarm_id=swarm_trace_id)

                    raise FailedUptest(msg)

    # Don't congratulate swarms that don't actually have any uptests.
    if test_counter > 0:
        send_event("Uptests passed", 'Uptests passed for swarm %s' % swarm,
                   tags=['success', 'uptest'], swarm_id=swarm_trace_id)
    else:
        send_event("No uptests!", 'No uptests for swarm %s' % swarm,
                   tags=['warning', 'uptest'], swarm_id=swarm_trace_id)

    # Also check for captured failures in the results
    correct_nodes = set(
        '%s:%s' % (host, procname.split('-')[-1])
        for host, results in uptest_results
        # results is now a dictionary keyed by procname
        for procname in results
    )

    callback = swarm_cleanup.subtask((swarm_id, swarm_trace_id))
    swarm_route.delay(swarm_id, list(correct_nodes), callback,
                      swarm_trace_id=swarm_trace_id)


@task
@event_on_exception(['route'])
def swarm_route(swarm_id, correct_nodes, callback=None, swarm_trace_id=None):
    """
    Given a list of nodes for the current swarm, make sure those nodes and
    only those nodes are in the swarm's routing pool, if it has one.
    """
    # It's important that the correct_nodes list be passed to this function
    # from the uptest finisher, rather than having this function build that
    # list itself, because if it built the list itself it couldn't be sure that
    # all the nodes had been uptested.  It's possible that one could have crept
    # in throuh a non-swarm deployment, for example.
    logger.info("[%s] Swarm %s route", swarm_trace_id, swarm_id)

    swarm = Swarm.objects.get(id=swarm_id)
    if swarm.pool:
        # There's just the right number of procs.  Make sure the balancer is up
        # to date, but only if the swarm has a pool specified.

        current_nodes = set(balancer.get_nodes(swarm.balancer, swarm.pool))

        correct_nodes = set(correct_nodes)

        new_nodes = correct_nodes.difference(current_nodes)

        stale_nodes = current_nodes.difference(correct_nodes)

        if new_nodes:
            balancer.add_nodes(swarm.balancer, swarm.pool, list(new_nodes))

        if stale_nodes:
            balancer.delete_nodes(swarm.balancer, swarm.pool,
                                  list(stale_nodes))

        msg = 'Routed swarm %s.  New nodes: %s' % (swarm, list(correct_nodes))
        send_event(str(swarm), msg, tags=['route'], swarm_id=swarm_trace_id)

    if callback is not None:
        subtask(callback).delay()


@task
def swarm_cleanup(swarm_id, swarm_trace_id):
    """
    Delete any procs in the swarm that aren't from the current release.
    """
    logger.info("[%s] Swarm %s cleanup", swarm_trace_id, swarm_id)

    swarm = Swarm.objects.get(id=swarm_id)
    all_procs = swarm.get_procs()
    current_procs = [p for p in all_procs if p.hash == swarm.release.hash]
    stale_procs = [p for p in all_procs if p.hash != swarm.release.hash]

    delete_subtasks = []

    # Only delete old procs if the deploy of the new ones was successful.
    if stale_procs and len(current_procs) >= swarm.size:
        for p in stale_procs:
            # We don't need to worry about removing these nodes from a pool at
            # this point, so just call delete_proc instead of swarm_delete_proc
            logger.info(
                "[%s] Swarm %s stale proc %s on host %s",
                swarm_trace_id, swarm_id, p.name, p.host.name)
            delete_subtasks.append(
                delete_proc.subtask((p.host.name, p.name),
                                    {'swarm_trace_id': swarm_trace_id})
            )

    if delete_subtasks:
        chord(delete_subtasks)(
            swarm_finished.subtask((swarm_id, swarm_trace_id,)))
    else:
        swarm_finished.delay([], swarm_id, swarm_trace_id)


@task
def swarm_finished(_results, swarm_id, swarm_trace_id):
    logger.info("[%s] Swarm %s finished", swarm_trace_id, swarm_id)

    swarm = Swarm.objects.get(id=swarm_id)
    title = msg = 'Swarm %s finished' % swarm
    send_event(title, msg,
               tags=['swarm', 'deploy', 'done'],
               swarm_id=swarm_trace_id)


@task
def swarm_delete_proc(swarm_id, hostname, procname, port, swarm_trace_id=None):
    # wrap the regular delete_proc, but first ensure the proc is removed from
    # the routing pool.  This is done on a per-proc basis because sometimes
    # it's called when deleting old procs, and other times it's called when we
    # just have too many of the current proc.  If it handles its own routing,
    # this function can be used in both places.
    logger.info(
        "[%s] Swarm %s delete proc on host %s",
        swarm_trace_id, swarm_id, hostname)

    swarm = Swarm.objects.get(id=swarm_id)
    if swarm.pool:
        node = '%s:%s' % (hostname, port)
        if node in balancer.get_nodes(swarm.balancer, swarm.pool):
            logger.info(
                "[%s] Swarm %s delete node %s",
                swarm_trace_id, swarm_id, node)
            balancer.delete_nodes(swarm.balancer, swarm.pool, [node])

    delete_proc(hostname, procname, swarm_trace_id=swarm_trace_id)


@task
def uptest_all_procs():
    print('Uptest all procs')
    # Fan out a task for each active host
    # callback post_uptest_all_procs at the end
    # Note: uptests can take a long time, so use .all() to fetch data
    # from DB immediately
    hosts = Host.objects.filter(active=True).all()

    # Only bother doing anything if there are active hosts
    if hosts:
        # Create a test run record.
        run = TestRun(start=timezone.now())
        run.save()
        print('Running test run_id={}'.format(run.id))

        def make_test_task(host):
            print('Creating test task for host={} run_id={}'.format(
                host.name, run.id))
            return uptest_host.subtask((host.name, run.id), expires=1800)
        chord((make_test_task(h) for h in hosts))(
            post_uptest_all_procs.subtask((run.id,)))

    else:
        print('No hosts to test')


@task
def post_uptest_all_procs(_results, test_run_id):
    print('Post uptest all procs')
    # record test run end time
    run = TestRun.objects.get(id=test_run_id)
    run.end = timezone.now()
    run.save()

    if run.has_failures():
        # Get just the failed TestResult objects.
        fail_results = run.tests.filter(passed=False)

        # Show output for each failed test in each failed result
        msg = '\n\n'.join(f.get_formatted_fails() for f in fail_results)

        print('Got failures')
        print(msg)
        send_event('scheduled uptest failures', msg,
                   tags=['scheduled', 'failed'])

    else:
        print('No failures')


@task
def _clean_host(hostname):
    with remote_settings(hostname):
        with always_disconnect(hostname):
            remote.clean_builds_folders()
            remote.clean_images_folders()
            remote.teardown_old_procs()
            remote.kill_orphans()


@task
def scooper():
    logger.info('Cleaning up hosts')
    for host in Host.objects.filter(active=True):
        _clean_host.apply_async((host.name,), expires=1800)

    logger.info('Free up old port locks')
    dt = timezone.now() - datetime.timedelta(days=PORTLOCK_MAX_AGE_DAYS)
    PortLock.objects.filter(created_time__lt=dt).delete()


@task
def clean_old_builds():
    # select all builds older than BUILD_EXPIRATION_DAYS where file is not
    # None
    if settings.BUILD_EXPIRATION_DAYS is not None:
        logger.info('Cleaning old builds')
        cutoff = (timezone.now() -
                  datetime.timedelta(days=settings.BUILD_EXPIRATION_DAYS))

        old_builds = Build.objects.filter(
            end_time__lt=cutoff, file__isnull=False).order_by('-end_time')
        old_builds = set(old_builds)

        # Now filter out any builds that are currently in use
        all_procs = set()
        for host in Host.objects.filter(active=True):
            all_procs.update(host.get_procs())

        builds_in_use = set()
        for p in all_procs:
            rs = Release.objects.filter(hash=p.hash)
            if rs:
                builds_in_use.add(rs[0].build)
        old_builds.difference_update(builds_in_use)

        # Filter out any builds that are still within BUILD_EXPIRATION_COUNT
        def is_recent(build):
            newer_builds = Build.objects.filter(id__gte=build.id,
                                                app=build.app)
            rcnt = newer_builds.count() < settings.BUILD_EXPIRATION_COUNT
            return rcnt
        old_builds.difference_update([b for b in old_builds if is_recent(b)])

        # OK, we now have a set of builds that are older than both our cutoffs,
        # and definitely not in use.  Delete their files to free up space.
        for build in old_builds:
            logger.info('Cleaning build %s', build)
            build.file.delete()
            build.status = 'expired'
            build.save()


def remote_settings(hostname):
    '''Context manager to set Fabric env suitably for remote calls.'''
    return fab_settings(
        host_string=hostname,
        abort_on_prompts=True,
        user=settings.DEPLOY_USER,
        password=settings.DEPLOY_PASSWORD,
        linewise=True)


@contextlib.contextmanager
def always_disconnect(host=None):
    """Disconnect from `host`. If `host` is None, disconnect from all hosts.

    See #18366.
    """
    try:
        yield
    finally:
        if host is None:
            logger.warning('Disconnecting from all hosts')
            fabric.network.disconnect_all()
        else:
            _disconnect_from_host(host)


def _disconnect_from_host(host):
    logger.info('Disconnecting from %s', host)
    if host in fabric.state.connections:
        fabric.state.connections[host].close()
        del fabric.state.connections[host]
        logger.info('Disconnected from %s', host)
    else:
        logger.warning('Not connected %s', host)


class tmpredis(object):
    def __enter__(self):
        self.conn = redis.StrictRedis(
            **utils.parse_redis_url(settings.EVENTS_PUBSUB_URL))
        return self.conn

    def __exit__(self, type, value, tb):
        self.conn.connection_pool.disconnect()


def lock_port(host, port):
    '''Acquire a PortLock on (host, port).

    `host` can either be a hostname or a db obj.
    '''
    logger.info('Acquiring port lock %s:%s', host, port)
    if isinstance(host, six.string_types):
        host = Host.objects.get(name=host)
    pl = PortLock(host=host, port=port)
    pl.save()


def unlock_port(host, port):
    '''Release the PortLock on (host, port).

    `host` can either be a hostname or a db obj.
    '''
    logger.info('Releasing port lock %s:%s', host, port)
    if isinstance(host, six.string_types):
        host = Host.objects.get(name=host)
    try:
        lock = PortLock.objects.get(host=host, port=int(port))
        lock.delete()
    except PortLock.DoesNotExist:
        pass


@contextlib.contextmanager
def unlock_port_ctx(host, port):
    """
    Context manager for removing a port lock on a host.

    `host` can either be a hostname or a db obj.
    """

    # This used just during deployment.  In general the host itself is the
    # source of truth about what ports are in use. But when deployments are
    # still in flight, port locks are necessary to prevent collisions.
    try:
        yield
    finally:
        unlock_port(host, port)
