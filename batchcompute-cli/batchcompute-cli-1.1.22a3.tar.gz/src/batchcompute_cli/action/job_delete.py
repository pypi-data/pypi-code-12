
# -*- coding:utf-8 -*-
from batchcompute import ClientError

from ..util import client,config,result_cache
from terminal import bold, magenta, white, blue, green,red, yellow, confirm

PROGRESS_LEN = 50

def del_job(jobId, yes=False):
    arr = jobId.split(',')


    t = []
    if config.isGod():
        for item in arr:
            id = result_cache.get(item, 'jobs')
            t.append(id)
    else:
        t = arr


    if yes:
        for item in t:
            __del_job(item)
    else:
        try:
            if confirm("Delete all these jobs:\n%s \nAre you sure" % red('\n'.join(t)), default=False):
                for item in t:
                    __del_job(item)
        except KeyboardInterrupt:
            print('')
            return


def __del_job(jobId):
    print(white('exec: bcs delete_job %s' % jobId))
    try:
       client.stop_job(jobId)
    except ClientError as e:
        if e.code == 'StateConflict':
            pass
        else:
            raise e

    client.delete_job(jobId)
    print(green('done'))
