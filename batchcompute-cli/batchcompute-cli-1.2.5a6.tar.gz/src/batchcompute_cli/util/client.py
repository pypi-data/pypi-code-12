from batchcompute import Client

from .config import getConfigs,COMMON
from batchcompute.utils import set_log_level

set_log_level("ERROR")

def _get_endpoint(region):
    domain = 'batchcompute.%s.aliyuncs.com' % region
    Client.register_region(region, domain)
    return domain


def _get_client(opt=None):
    opt = opt or getConfigs(COMMON, ['region', 'accesskeyid','accesskeysecret','version'])
    if not opt or not opt.get('accesskeyid'):
        raise Exception('You need to login first')

    c = Client(_get_endpoint(opt.get('region')),
        opt.get('accesskeyid'), opt.get('accesskeysecret'))

    if opt.get('version'):
        c.version = opt.get('version')
    return c

def check_client(opt):
    client = _get_client(opt)
    client.list_jobs("",1)


def list_clusters():
    client = _get_client()
    arr = __list_clusters(client)
    return {'Items':arr,'Marker':''}

def __list_clusters(client, marker='', maxItemCount=100):
    t = []
    result = client.list_clusters(marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_clusters(client,result.NextMarker,maxItemCount)
        t = t + arr
    return t

def get_cluster(cluster_id):
    client = _get_client()
    return client.get_cluster(cluster_id)

def delete_cluster(cluster_id):
    client = _get_client()
    return client.delete_cluster(cluster_id)

def create_cluster(clusterDesc):
    client = _get_client()
    return client.create_cluster(clusterDesc)

def change_cluster_vmcount(cluster_id, groupName, vmCount):
    client = _get_client()
    return client.change_cluster_desired_vm_count(cluster_id, **{groupName: int(vmCount)})




def list_jobs():
    client = _get_client()
    arr = __list_jobs(client)
    return {'Items':arr,'Marker':''}

def __list_jobs(client, marker='', maxItemCount=100):
    t = []
    result = client.list_jobs(marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_jobs(client, result.NextMarker, maxItemCount)
        t = t + arr
    return t




def get_job(job_id):
    client = _get_client()
    return client.get_job(job_id)

def get_job_description(job_id):
    client = _get_client()
    return client.get_job_description(job_id)

def list_tasks(job_id):
    client = _get_client()
    arr = __list_tasks(client, job_id)
    return {'Items':arr,'Marker':''}

def __list_tasks(client,job_id, marker='', maxItemCount=100):
    t = []
    result = client.list_tasks(job_id, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_tasks(client, job_id, result.NextMarker, maxItemCount)
        t = t + arr
    return t



def list_instances(job_id, task_name):
    client = _get_client()
    arr = __list_instances(client, job_id, task_name)
    return {'Items':arr,'Marker':''}

def __list_instances(client, job_id, task_name, marker='', maxItemCount=100):
    t = []
    result = client.list_instances(job_id, task_name, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_instances(client, job_id, task_name, result.NextMarker, maxItemCount)
        t = t + arr
    return t


def get_task(job_id, task_name):
    client = _get_client()
    return client.get_task(job_id, task_name)


def get_instance(job_id, task_name, instance_id):
    client = _get_client()
    return client.get_instance(job_id, task_name, instance_id)




def change_job_priority(job_id, priority):
    client = _get_client()
    return client.change_job_priority(job_id, priority)


def start_job(job_id):
    client = _get_client()
    return client.start_job(job_id)


def stop_job(job_id):
    client = _get_client()
    return client.stop_job(job_id)

def delete_job(job_id):
    client = _get_client()
    return client.delete_job(job_id)

def create_job(jobDesc):
    client = _get_client()
    return client.create_job(jobDesc)


def __items2list(items):
    t=[]
    for item in items:
        m = {}
        for k in item.keys():
            m[k] = item.get(k)
        t.append(m)
    return t