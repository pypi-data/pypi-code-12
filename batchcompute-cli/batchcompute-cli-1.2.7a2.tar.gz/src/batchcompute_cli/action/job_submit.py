
# -*- coding:utf-8 -*-

from ..util import client,config, formater, oss_client,util
from terminal import green
import json
import os
import uuid
import tarfile
from ..const import CMD


try:
    import ConfigParser
except:
    import configparser as ConfigParser


DEFAULT='DEFAULT'

def submit(cmd=None, job_name=None, description=None, cluster=None, timeout=None, nodes=None,
           force=False, docker=None, pack=None, env=None, read_mount=None, write_mount=None, mount=None,
           file=None, priority=None, disk=None, show_json=False):

    if cmd == None and file == None  or cmd!=None and cmd.startswith('-'):
        print('\n  type "%s sub -h" for more\n' % CMD)
        return

    job_desc = trans_file_to_job_desc(file)

    opt = {
        'cmd': cmd,
        'job_name': job_name,
        'description': description,
        'cluster': cluster,
        'disk': disk,
        'timeout': timeout,
        'nodes' : nodes,
        'force': force,

        'priority': priority,

        'docker': docker,
        'pack': pack,
        'env': env,

        'read_mount': read_mount,
        'write_mount': write_mount,
        'mount': mount
    }

    job_desc = fix_by_opt(job_desc, opt)

    deal_with_pack(job_desc, show_json)

    if show_json:
        print(json.dumps(job_desc, indent=4))
    else:
        result = client.create_job(job_desc)

        if result.StatusCode==201:
            print(green('Job created: %s' % result.Id))

def deal_with_pack(desc, show_json):
    pre_oss_path = config.get_oss_path()
    rand = gen_rand_id()

    tasks = desc['DAG']['Tasks']

    m = {}
    for (task_name,task_desc) in tasks.items():
        task_desc['Parameters']['StdoutRedirectPath'] = '%s%s/logs/' % (pre_oss_path,rand)
        task_desc['Parameters']['StderrRedirectPath'] = '%s%s/logs/' % (pre_oss_path,rand)

        pack = task_desc.get('pack')

        if pack:

            if not m.get(pack):
                if not m:
                    package_path = '%s%s/worker.tar.gz' % (pre_oss_path, rand)
                else:
                    package_path = '%s%s/worker_%s.tar.gz' % (pre_oss_path, rand, task_name)
                m[pack] = package_path

                # pack upload
                if not show_json:
                    pack_upload(pack, package_path)


            task_desc['Parameters']["Command"]['PackagePath'] = m[pack]
            del task_desc['pack']
        else:
            task_desc['Parameters']["Command"]['PackagePath'] = ''



    return desc


def pack_upload(pack, package_path):

    if ',' in pack:
        print('packing multi-files..')
        arr = pack.split(',')
        build_tar_from_arr_and_upload(arr, package_path)
    else:
        folder_path = formater.get_abs_path(pack)
        if os.path.isdir(folder_path):
            print('packing folder..')
            build_tar_from_dir_and_upload(folder_path, package_path)
        else:
            print('packing a single file..')
            build_tar_from_arr_and_upload([pack],package_path)

def fix_by_opt(desc, opt):

    if opt.get('job_name'):
        desc['Name'] = opt['job_name']
    if opt.get('description'):
        desc['Description'] = opt['description']
    if opt.get('priority'):
        desc['Priority'] = trans_priority(opt['priority'])
    if opt.get('force'):
        desc['JobFailOnInstanceFail'] = not opt['force']



    tasks = desc['DAG']['Tasks']
    for (task_name,task_desc) in tasks.items():

        if opt.get('cmd'):
            task_desc['Parameters']['Command']['CommandLine']=opt['cmd']

        if not task_desc['Parameters']['Command'].get('CommandLine'):
            raise Exception('Missing required option: cmd')


        if opt.get('timeout'):
            task_desc['Timeout'] = trans_timeout(opt['timeout'])
        if opt.get('nodes'):
            task_desc['InstanceCount'] = trans_nodes(opt['nodes'])
        if opt.get('cluster'):
            extend(task_desc, trans_cluster(opt['cluster']))
        if opt.get('disk') and task_desc.get('AutoCluster'):
            task_desc['AutoCluster']['Configs'] = {'Disks': opt['disk']}

        if opt.get('docker'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_docker(opt['docker']))
        if opt.get('env'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_env(opt['env']))
        if opt.get('mount'):
            mount_m = trans_mount(opt['mount'])
            extend(task_desc['InputMapping'], mount_m)
            extend(task_desc['OutputMapping'], reverse_kv(mount_m))
        if opt.get('read_mount'):
            extend(task_desc['InputMapping'], trans_mount(opt['read_mount']))
        if opt.get('write_mount'):
            extend(task_desc['OutputMapping'], reverse_kv(trans_mount(opt['write_mount'])))

        # cache
        if opt.get('pack'):
            task_desc['pack'] = opt['pack']

    return desc



########################################

def trans_file_to_job_desc(file):
    cf = ConfigParser.ConfigParser()
    # parse file
    if not file:
        desc = gen_job_desc()
        desc['DAG']['Tasks']['task'] = gen_task_desc()
        return desc

    # else
    cfg_path = os.path.join(os.getcwd(), file)
    if not os.path.exists(cfg_path):
        raise Exception('Invalid file: %s' % cfg_path)
    cf.read(cfg_path)


    desc = gen_job_desc()

    default_options = cf.defaults()

    if default_options:
        if default_options.get('job_name'):
            desc['Name'] = default_options['job_name']
        if default_options.get('description'):
            desc['Description'] = default_options['description']
        if default_options.get('priority'):
            desc['Priority'] = trans_priority(default_options['priority'])
        if default_options.get('force'):
            desc['JobFailOnInstanceFail'] = not cf.getboolean(DEFAULT,'force')

        if default_options.get('deps'):
            desc['DAG']['Dependencies'] = trans_deps(cf.get(DEFAULT,'deps'))


    # without DEFAULT
    secs = cf.sections()

    for sec in secs:
        task_desc = gen_task_desc()


        # fix job fields in old version
        #################################
        if cf.has_option(sec,'job_name'):
            desc['Name'] = cf.get(sec,'job_name')
        if cf.has_option(sec,'description'):
            desc['Description'] = cf.get(sec,'description')
        if cf.has_option(sec,'priority'):
            desc['Priority'] = trans_priority(cf.get(sec,'priority'))
        if cf.has_option(sec,'force'):
            desc['JobFailOnInstanceFail'] = not cf.getboolean(sec,'force')
        #################################

        ## extend by default options
        if default_options:
            ####################################
            if cf.has_option(DEFAULT,'env'):
                extend(task_desc['Parameters']['Command']['EnvVars'], trans_env(cf.get(DEFAULT,'env')))
            if cf.has_option(DEFAULT,'docker'):
                extend(task_desc['Parameters']['Command']['EnvVars'], trans_docker(cf.get(DEFAULT,'docker')))

            if cf.has_option(DEFAULT,'mount'):
                mount_m = trans_mount(cf.get(DEFAULT,'mount'))
                extend(task_desc['InputMapping'], mount_m)
                extend(task_desc['OutputMapping'], reverse_kv(mount_m))
            if cf.has_option(DEFAULT,'read_mount'):
                r_mount_m = trans_mount(cf.get(DEFAULT,'read_mount'))
                extend(task_desc['InputMapping'], r_mount_m)
            if cf.has_option(DEFAULT,'write_mount'):
                w_mount_m = trans_mount(cf.get(DEFAULT,'write_mount'))
                extend(task_desc['OutputMapping'], reverse_kv(w_mount_m))
            ###################################




        if cf.has_option(sec, "cmd"):
            task_desc['Parameters']['Command']['CommandLine']= cf.get(sec,'cmd')
        # else:
        #     raise Exception('Missing required option: cmd')


        # cache
        if cf.has_option(DEFAULT, "pack"):
            task_desc['pack']=  cf.get(DEFAULT,'pack')
        if cf.has_option(sec, "pack"):
            task_desc['pack']=  cf.get(sec,'pack')

        if cf.has_option(sec, "timeout"):
            task_desc['Timeout']= trans_timeout(cf.getint(sec,'timeout'))
        if cf.has_option(sec,'nodes'):
            task_desc['InstanceCount']=trans_nodes(cf.getint(sec,'nodes'))

        if cf.has_option(sec,'cluster'):
            extend(task_desc, trans_cluster(cf.get(sec,'cluster')) )

        if cf.has_option(sec, 'disk') and task_desc.get('AutoCluster'):
            task_desc['AutoCluster']['Configs'] = {'Disks': trans_disk(cf.get(sec, 'disk')) }


        if cf.has_option(sec,'env'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_env(cf.get(sec,'env')))
        if cf.has_option(sec,'docker'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_docker(cf.get(sec,'docker')))

        if cf.has_option(sec,'mount'):
            mount_m = trans_mount(cf.get(sec,'mount'))
            extend(task_desc['InputMapping'], mount_m)
            extend(task_desc['OutputMapping'], reverse_kv(mount_m))
        if cf.has_option(sec,'read_mount'):
            r_mount_m = trans_mount(cf.get(sec,'read_mount'))
            extend(task_desc['InputMapping'], r_mount_m)
        if cf.has_option(sec,'write_mount'):
            w_mount_m = trans_mount(cf.get(sec,'write_mount'))
            extend(task_desc['OutputMapping'], reverse_kv(w_mount_m))

        desc['DAG']['Tasks'][sec]= task_desc

    return desc

####################################################



def extend(obj, obj2):
    for k in obj2:
        obj[k] = obj2[k]
    return obj

def trans_deps(deps):
    # A->b,c;d->e,f
    parts = deps.strip(';').split(';')
    m = {}
    for part in parts:
        [k,v] = part.split('->')
        m[k] = [x.strip() for x in v.split(',')]
    return m

def trans_cluster(cluster):
    return util.parse_cluster_cfg(cluster)

def override_opt(opt, file):
    # asd
    for (k,v) in file.items():
        if not opt.get(k):
           opt[k] = v
    return opt

def trans_nodes(n):
    try:
        n = int(n)
        return n if n > 0 else 1
    except:
        return 1

def trans_timeout(n):
    try:
        n = int(n)
        return n if n > 0 else 172800
    except:
        return 172800



def trans_docker(docker=None, ignoreErr=False):
    return util.trans_docker(docker, ignoreErr)

def trans_env(s):
    if not s:
        return {}
    arr = s.split(',')
    env = {}
    for item in arr:
        [k,v]=item.split(':',1)
        env[k]=v
    return env


def trans_mount(s):
    return util.trans_mount(s)


def trans_priority(p=None):
    try:
        return int(p)
    except:
        return 1

def trans_disk(disk):
    return util.trans_disk(disk)

#######################################

def reverse_kv(m):
    m2={}
    for k,v in m.items():
        m2[v]=k
    return m2

def gen_rand_id():
    return uuid.uuid1()





def build_tar_from_dir_and_upload(folder_path, oss_path):
    '''
    pack program files, and upload to oss_path
    :param folder_path:
    :param oss_path:
    :return:
    '''

    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

    if os.path.exists(dist):
        os.remove(dist)

    # tar
    print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:

        full_folder_path = formater.get_abs_path(folder_path)
        full_folder_path = full_folder_path.rstrip('/')+'/'
        print('base folder: %s' % full_folder_path)

        for root,dir,files in os.walk(folder_path):
            for file in files:
                fullpath=os.path.join(root,file)
                fullpath = formater.get_abs_path(fullpath)
                fname = fullpath[len(full_folder_path):]
                print('add %s' % fname)
                tar.add(fullpath, arcname=fname)

    # upload
    print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)


def build_tar_from_arr_and_upload(arr, oss_path):
    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

    if os.path.exists(dist):
        os.remove(dist)

     # tar
    print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:
        for file in arr:
            fullpath = formater.get_abs_path(file)
            print('add %s' % file)
            tar.add(fullpath, arcname=os.path.basename(fullpath))

    # upload
    print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)



def gen_task_desc():
    return extend({
        "OutputMapping": {},
        "Timeout": 172800,
        "InputMapping": {},
        "LogMapping": {},
        "InstanceCount": 1,
        "ClusterId": "",
        "AutoCluster": {},
        "MaxRetryCount": 0,
        "Parameters": {
            "StderrRedirectPath": "",
            "InputMappingConfig": {
                #"Locale": "GBK",
                "Lock": False
            },
            "StdoutRedirectPath": "",
            "Command": {
                "EnvVars": {},
                "CommandLine": "",
                "PackagePath": ""
            }
        },
        "WriteSupport": True
    },trans_cluster(None))


def gen_job_desc():
    return {
        "DAG": {
            "Tasks": { },
            "Dependencies": {}
        },
        "Description": "BatchCompute cli job",
        "JobFailOnInstanceFail": True,
        "Priority": 1,
        "Type": "DAG",
        "Name": "cli-job"
    }