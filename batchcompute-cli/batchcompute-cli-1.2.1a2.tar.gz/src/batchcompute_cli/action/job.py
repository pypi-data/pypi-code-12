# -*- coding:utf-8 -*-

from ..util import client, oss_client, formater, list2table, result_cache, dag, util
from terminal import bold, magenta, white, blue, green, red, yellow, confirm
from oss2.exceptions import NoSuchKey,NoSuchBucket
from ..const import CMD

PROGRESS_LEN = 50


def all(jobId=None, taskName=None, instanceId=None,  description=False, all=False, top=10, state=None, id=None, name=None):
    if jobId:
        if instanceId:
            getInstanceDetail(jobId, taskName, instanceId)
        elif taskName:
            getTaskDetail(jobId, taskName)
        else:
            getJobDetail(jobId, description)

    else:
        list(top, all, state, id, name)


def list(num,all, state, jobId, jobName):

    num = int(num)

    tip= []
    result = client.list_jobs()

    arr = formater.items2arr(result.get('Items'))
    result_len = len(arr)

    # state filter
    if state:
        arr = formater.filter_list(arr, {'State': state.split(',')})
        tip.append('-s %s' % state)

    # like filter
    if jobId:
        arr = formater.filter_list(arr, {'Id': {'like': jobId}})
        tip.append('-i %s' % jobId)

    if jobName:
        arr = formater.filter_list(arr, {'Name': {'like': jobName}})
        tip.append('-n %s' % jobName)

    arr = formater.format_date_in_arr(arr, ['CreationTime', 'StartTime', 'EndTime'])

    # sort
    arr = sort_job_list(arr)

    has_more = not all and len(arr) > num

    # num
    if not all and num:
        arr = arr[:num]

    print(white('exec: bcs j -t %s%s' % ( num, ' '.join(tip) )))


    for item in arr:
        item['Counts'] = calc_metric_count(item['TaskMetrics'])
        #item['Description'] = formater.sub(item.get('Description'))

    result_cache.save(arr, 'Id', 'jobs')

    print('%s' % bold(magenta('Jobs:')))
    list2table.print_table(arr, ['Id', 'Name', ('State', 'State', formater.get_job_state), 'Counts',
                              ('CreationTimeFromNow', 'Created'), 'StartTime', 'EndTime','Elapsed'])

    cache_len = len(arr)
    cache_str =white('(cache %s %s)' %  (cache_len, 'rows' if cache_len>1 else 'row' ) )
    print('%s  %s' %(green('Total: %s' % result_len), cache_str) )

    if has_more:
        print(white('\n  append -t <num> to show more, or -a to show all\n'))

    print(white('  type "%s j <jobId|No.>" to show job detail\n' % (CMD)))

def getJobDetail(jobId, descOnly):
    jobId = result_cache.get(jobId, 'jobs')

    print(white('exec: bcs j %s%s' % (jobId, ' -d' if descOnly else '')))

    desc = client.get_job_description(jobId)

    if descOnly:
        print(desc)
        return

    result = client.get_job(jobId)
    result = formater.to_dict(result)
    [result] = formater.format_date_in_arr([result], ['CreationTime', 'StartTime', 'EndTime'])


    t = [{
        'a': '%s: %s' % (blue('Id'), result.get('Id')),
        'b': '%s: %s' % (blue('Name'), result.get('Name')),
        'c': '%s: %s' % (blue('State'), formater.get_job_state(result.get('State')))
    }, {
        "a": '%s: %s' % (blue('JobFailOnInstanceFail'), desc.get('JobFailOnInstanceFail')),
        "b": '%s: %s' % (blue('Type'), desc.get('Type')),
        "c": '%s: %s' % (blue('Priority'), desc.get('Priority'))
    }, {
        "a": '%s: %s    %s: %s' % (blue('Created'), result.get('CreationTimeFromNow') ,blue('Elapsed'), result.get('Elapsed') ),
        "b": '%s: %s' % (blue('StartTime'),  result.get('StartTime')),
        "c": '%s: %s' % (blue('EndTime'),  result.get('EndTime')),
    }]


    print('%s' % bold(magenta('Job:')))
    list2table.print_table(t, cols=['a', 'b', 'c'], show_no=False, show_header=False)


    # description
    if desc.get('Description'):
        print('  %s: %s' % (blue('Description'), desc.get('Description') or ''))


    # task list
    tasks = client.list_tasks(jobId)

    arr = formater.items2arr(tasks.get('Items'))

    arr = formater.format_date_in_arr(arr, ['StartTime', 'EndTime'])

    # calc deps
    deps = util.get_task_deps(desc.get('DAG'))
    matric = dag.sortIndex(deps)

    # dag
    if len(arr)>1:
        print('%s' % bold(magenta('DAG:')))
        dag.draw(deps, matric)

     # task list continue
    for item in arr:
        item['Counts'] = calc_metric_count(item['InstanceMetrics'])
        task_desc = desc.DAG.Tasks[item['TaskName']]

        item['Cluster'] = util.get_cluster_str(task_desc)

    arr = util.sort_task_by_deps(arr, matric)

    # cache
    result_cache.save(arr, 'TaskName', 'tasks')

    print('%s' % bold(magenta('Tasks:')))
    list2table.print_table(arr, cols=['TaskName',('State', 'State', formater.get_job_state), 'Counts', 'StartTime', 'EndTime', 'Elapsed','Cluster'])

    arrlen = len(arr)
    cache_str = white('(cache %s %s)' %  (arrlen, 'rows' if arrlen>1 else 'row' ) )
    print(cache_str)

    print(white('\n  type "%s j <jobId|No.> <taskName|No.>" to show task detail\n' % CMD))

def getTaskDetail(jobId, taskName):
    jobId = result_cache.get(jobId, 'jobs')
    taskName = result_cache.get(taskName, 'tasks')

    print(white('exec: bcs j %s %s' %  (jobId,taskName) ))

    jobDesc = client.get_job_description(jobId)

    taskInfo = client.get_task(jobId, taskName)

    taskInfo = formater.to_dict(taskInfo)

    taskInfo['Counts'] = calc_metric_count(taskInfo['InstanceMetrics'])
    taskDesc = jobDesc.DAG.Tasks[taskInfo['TaskName']]

    taskInfo['Cluster'] = util.get_cluster_str(taskDesc)

    arr = formater.format_date_in_arr([taskInfo], [ 'StartTime', 'EndTime'])


    # task
    print('%s' % bold(magenta('Task:')))
    list2table.print_table(arr, cols=['TaskName',('State', 'State', formater.get_job_state), 'Counts', 'StartTime', 'EndTime','Elapsed','Cluster'], show_no=False)


    # task description
    print('%s' % bold(magenta('Task Description:')))

    command = formater.to_dict(taskDesc.Parameters.Command)

    print('%s: %s    %s: %s    %s: %s' %(  blue('Timeout'), taskDesc.Timeout, blue('MaxRetryCount'), taskDesc.MaxRetryCount, blue('WriteSupport'), taskDesc.WriteSupport, ))

    print(blue('Command:'))
    print('  %s: %s' % (blue('CommandLine') , command.get('CommandLine')))
    if command.get('PackagePath'):
        print('  %s: %s' % (blue('PackagePath') , command.get('PackagePath')))
    if command.get('EnvVars'):
        print(blue('  EnvVars:'))
        for (k,v) in command['EnvVars'].items():
            print('    %s: %s' % (bold(k),v))


    print('%s: %s' % ( blue('InputMappingConfig:'),formater.to_dict( taskDesc.Parameters.InputMappingConfig) ))
    print('%s: %s' % ( blue('StdoutRedirectPath:'), taskDesc.Parameters.StdoutRedirectPath ))
    print('%s: %s' % ( blue('StderrRedirectPath:'), taskDesc.Parameters.StderrRedirectPath ))


    if taskDesc.InputMapping:
        print(blue('InputMapping:'))
        for (k,v) in taskDesc.InputMapping.items():
            print('  %s: %s' % (bold(k),v))

    if taskDesc.OutputMapping:
        print(blue('OutputMapping:'))
        for (k,v) in taskDesc.OutputMapping.items():
            print('  %s: %s' % (bold(k),v))

    if taskDesc.LogMapping:
        print(blue('LogMapping:'))
        for (k,v) in taskDesc.LogMapping.items():
            print('  %s: %s' % (bold(k),v))

    # instances

    insts = client.list_instances(jobId, taskName)

    print('%s' % bold(magenta('Instances:')))

    t = []
    c = 0
    if len(insts['Items']) > 10:

        for ins in insts['Items']:
            t.append('%s. %s(%s%%)' % (ins.get('InstanceId'), formater.get_job_state(ins.get('State')), ins.get('Progress')))
            c += 1
            if len(t)==5:
                print('    '.join(t))
                t=[]
                c=0
        if c>0:
            print('    '.join(t))
    else:
        arr = formater.format_date_in_arr(insts['Items'], [ 'StartTime', 'EndTime'])
        list2table.print_table(arr, ['InstanceId',('State', 'State', formater.get_job_state)
                                     , ('Progress','Progress',lambda s:'%s%%' % s), 'RetryCount'
            ,'StartTime','EndTime','Elapsed'],show_no=False)

    print(white('\n  type "%s j <jobId|No.> <taskName|No.> <instanceId>" to show instance detail\n' % CMD))

def getInstanceDetail(jobId, taskName, instanceId):
    jobId = result_cache.get(jobId, 'jobs')
    taskName = result_cache.get(taskName, 'tasks')

    print(white('exec: bcs j %s %s %s' %  (jobId,taskName, instanceId) ))

    ins = client.get_instance(jobId, taskName, instanceId)

    arr = formater.format_date_in_arr([formater.to_dict(ins)], ['CreationTime', 'StartTime', 'EndTime'])

    print('%s' % bold(magenta('Instance:')))
    list2table.print_table(arr, cols=['InstanceId',('State', 'State', formater.get_job_state), ('Progress','Progress',lambda s:'%s%%' % s), 'RetryCount','StartTime','EndTime','Elapsed' ], show_no=False)

    stdout_path = formater.fix_log_path(ins.StdoutRedirectPath,jobId,taskName, instanceId, 'stdout')
    stderr_path = formater.fix_log_path(ins.StderrRedirectPath,jobId,taskName, instanceId, 'stderr')

    print('%s: %s' % (blue('StdoutRedirectPath'), stdout_path ))
    print('%s: %s' % (blue('StderrRedirectPath'), stderr_path ))

    if ins.Result and ins.Result.Detail:
        print('%s' % bold(magenta('Result:')))
        print('  %s: %s' % (blue('ExitCode'), ins.Result.ExitCode ))
        print('  %s: %s' % (blue('ErrorCode'), red(ins.Result.ErrorCode) ))
        print('  %s: %s' % (blue('ErrorMessage'), red(ins.Result.ErrorMessage) ))
        print('  %s: %s' % (blue('Detail'), red(ins.Result.Detail) ))

    try:
        showLog(ins.StderrRedirectPath,jobId,taskName, instanceId, 'stderr')
    except Exception as e:
        if not isinstance(e, NoSuchKey) and not isinstance(e, NoSuchBucket):
            raise e
        try:
            showLog(ins.StdoutRedirectPath,jobId,taskName, instanceId, 'stdout')
        except Exception as e:
            if not isinstance(e, NoSuchKey) and not isinstance(e, NoSuchBucket):
                raise e

    print(white('\n  If you want to download these logs, type "%s log -h" for more\n' % CMD))

def showLog(osspath, jobId, taskName, instanceId, logType):

    osspath = formater.fix_log_path(osspath ,jobId,taskName, instanceId, logType)
    content = oss_client.get_data(osspath)

    print('%s' % bold(magenta('Log Content:')))
    print(magenta('%s%s%s' % ('-'*20, logType, '-'*20)  ))
    if isinstance(content, bytes):
        content = str(content.decode('utf8'))

    if logType == 'stdout':
        print(green(content))
    else:
        print(red(content))
    print(magenta('-'*46))


def calc_metric_count(metric):
    g = metric
    total = g['RunningCount'] + g['WaitingCount'] + g['FinishedCount'] + g['StoppedCount']+g['FailedCount']
    count = g['FinishedCount'] + g['FailedCount']

    return '%s / %s' % (count, total)

def sort_job_list(arr):
    finished_arr = []
    unfinished_arr = []

    for n in arr:
        if n['State'] == 'Running' or n['State'] == 'Waiting':
            unfinished_arr.append(n)
        else:
            finished_arr.append(n)

    finished_arr = formater.order_by(finished_arr, ['CreationTime'], True)
    unfinished_arr = formater.order_by(unfinished_arr, ['StartTime','CreationTime'], True)

    return unfinished_arr + finished_arr


