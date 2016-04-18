from terminal import red,confirm,blue,white
from ..util import formater,config,oss_client

def delete(osspath, yes=False):

    if osspath.find('oss://') != 0:
        osspath = '%s%s' % (config.get_oss_path(), osspath)

    # list
    (bucket,key) = oss_client.parse_oss_path(osspath)
    (arr, pre_arr, bucket_tool) = oss_client.list(osspath)

    t=[]
    show_keys=[]
    klen = len(key)

    if len(arr)>0:
        for k in arr:
            t.append(k.key)
            if k.key!=key:
                show_keys.append(k.key[klen:])
            else:
                show_keys.append('.(%s)' % white(key))
    tlen = len(t)


    if tlen > 0:
        msg = "%s %s\n%s\n  %s\n%s" % (blue('Delete oss path' ),
                                osspath,
                                   'Found %s files' % tlen,
                               '\n  '.join(show_keys),
                               red('Delete all these %s files?' % tlen))
    else:
        print('Not found')
        return

    if yes or confirm(msg):
        if tlen>0:
            bucket_tool.batch_delete_objects(t)
        bucket_tool.delete_object(key)

