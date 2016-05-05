from ec2ssh2.config import Config
from ec2ssh2.ec2_searcher import EC2Searcher
from ec2ssh2 import exceptions
import os
import random
def get_tags(instance):
    return {tag['Key']: tag['Value'] for tag in instance.tags}

if __name__ == '__main__':
    conf = Config()
    searcher = EC2Searcher()
    instances = list(searcher.search(
        tags=conf.tag_filters,
        vpc_scopes=[conf.vpc_scope]
    ))
    for instance in instances:
        name = get_tags(instance).get('Name', 'NO NAME')
        print name, instance.instance_id, instance.public_dns_name
    if not instances:
        raise exceptions.NoInstancesFound()
    instance = random.choice(instances)
    args = []
    if conf.key_file_path:
        args.extend(['-i', conf.key_file_path])
    target = "%s@%s" % (conf.remote_user, instance.public_dns_name)
    args.append(target)
    name = 'ec2ssh2 : %s' % target
    os.execlp("ssh", name, *args)
