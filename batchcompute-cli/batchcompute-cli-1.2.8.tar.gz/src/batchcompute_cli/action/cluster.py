# -*- coding:utf-8 -*-

from ..util import client, formater, list2table, result_cache, it
from terminal import bold, magenta, white, blue, green,red, yellow, confirm
from ..const import CMD

PROGRESS_LEN = 70

def all(clusterId=None, description=False):
    if clusterId:
        get(clusterId, description)
    else:
        list()


def list():

    result = client.list_clusters()

    arr = formater.items2arr(result.get('Items'))

    result_len = len(arr)

    arr = formater.format_date_in_arr(arr, ['CreationTime'])

    # sort
    arr = sort_cluster_list(arr)

    for item in arr:
        total =0
        actual_count = 0
        for k in item['Groups']:
            g = item['Groups'][k]
            actual_count += g['ActualVMCount']
            total += g['DesiredVMCount']
        item['Counts'] = '%s / %s' % (actual_count,total)
        #item['Description'] =  formater.sub(item['Description'],10)


    result_cache.save(arr, 'Id', 'clusters')

    #print(white('RequestId: %s' % result.get('RequestId')))
    print('%s' % bold(magenta('Clusters:')))
    list2table.print_table(arr,['Id','Name',('State','State', formater.get_cluster_state),'Counts','CreationTime',('CreationTimeFromNow','FromNow')])

    arrlen = len(arr)
    cache_str =white('(cache %s %s)' %  (arrlen, 'rows' if arrlen>1 else 'row' ) )
    print('%s %s' % ( green('Total: %s' % result_len), cache_str))


    print(white('\n  type "%s c <Id|No.>" to show cluster detail\n' % (CMD)))

def get(clusterId,descOnly=False):
    clusterId = result_cache.get(clusterId, 'clusters')

    print(white('exec: bcs c %s' % clusterId))
    result = client.get_cluster(clusterId)

    if descOnly:
        print(result)
        return

    arr = [{
        'a': '%s: %s' % (blue('Id'), result.get('Id')),
        'b': '%s: %s' % (blue('Name'), result.get('Name')),
        'c': '%s: %s' % (blue('State'), formater.get_cluster_state(result.get('State')))
    },{
        'a': '%s: %s' % (blue('ImageId'), result.get('ImageId')),
        #'b': '%s: %s' % (blue('InstanceType'),  result.get('InstanceType')),
        'c': '',
        'b': '%s: %s' % (blue('Created'), formater.from_now(result.get('CreationTime')))
    }]
    print('%s' % bold(magenta('Cluster:')))
    list2table.print_table(arr, ['a','b','c'], show_no=False, show_header=False)

    # disks
    disks = result.Configs.Disks
    print(blue('Disks:'))
    if disks.get('SystemDisk'):
        print('  |--System Disk: %s (%s) %sGB' % ('/', blue(disks['SystemDisk']['Type']), disks['SystemDisk']['Size']) )
    if disks.get('DataDisk') and disks['DataDisk'].get('MountPoint'):
        print('  |--Data Disk: %s (%s) %sGB' % (disks['DataDisk']['MountPoint'], blue(disks['DataDisk']['Type']), disks['DataDisk']['Size'] ))
    print('')

    # description
    if result.get('Description'):
        print('%s: %s' % (blue('Description'), result.get('Description')))


    # groups
    groups = []
    total_desired_vm_count = 0
    for groupName in result.Groups:
        v = formater.to_dict(result.Groups[groupName])
        v['Name'] = groupName
        v['VMCount'] = '%s / %s' % (v['ActualVMCount'],v['DesiredVMCount'])
        ins = it.get_ins_type_map().get(v['InstanceType'])
        if ins:
            v['InstanceType/cpu/mem'] = '%s, %sCores, %sGB' % (v['InstanceType'], ins['cpu'], ins['memory'])
        else:
            v['InstanceType/cpu/mem'] = v['InstanceType']
        groups.append(v)
        total_desired_vm_count = total_desired_vm_count + v['DesiredVMCount']


    result_cache.save(groups, 'Name', 'groups')


    # metric
    print(blue('Metrics:'))
    metrics = formater.to_dict(result.get('Metrics'))
    metrics['UnallocatedCount'] = total_desired_vm_count - metrics['StartingCount'] - metrics['RunningCount'] - metrics['StoppingCount'] - metrics['StoppedCount']
    cols = [('Starting',blue), ('Running',green), ('Stopping',yellow), ('Stopped',red),('Unallocated',white)]
    t = []
    p = []

    for k in cols:
        t.append( (('  %s: %s' % (k[1](k[0]), metrics.get('%sCount' % k[0])) )) )
        plen = metrics.get('%sCount' % k[0]) * PROGRESS_LEN/total_desired_vm_count
        plen = int(plen)
        p.append(  str(k[1]('=' * plen)) if plen>0 else '' )
    print('  '.join(t))


    # metric progress
    print(' | %s |' % (''.join(p)) )

    # user data
    ud = result.get('UserData')
    if ud:
        print('%s' % (blue('User Data:')))
        for (k,v) in ud.items():
            print('  %s : %s' % (k,v))

    # OperationLogs
    print('%s:\n  %s' % (blue('Operation Logs'),   '\n  '.join(result.get('OperationLogs')) ))

    # print groups
    print('%s' % bold(magenta('Groups:')))
    list2table.print_table(groups, ['Name','VMCount','InstanceType/cpu/mem', 'ResourceType'])

    #print(result)

def sort_cluster_list(arr):
    others_arr = []
    deleting_arr = []

    for n in arr:
        if n['State'] == 'Deleting':
            deleting_arr.append(n)
        else:
            others_arr.append(n)

    deleting_arr = formater.order_by(deleting_arr, ['CreationTime'], True)
    others_arr = formater.order_by(others_arr, ['CreationTime'], True)

    return deleting_arr + others_arr

