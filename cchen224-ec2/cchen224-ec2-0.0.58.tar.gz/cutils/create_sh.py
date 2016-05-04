

servers = ['ec2-54-213-197-135',
           'ec2-54-191-147-98',
           'ec2-54-187-221-97',
           'ec2-54-200-71-123',
           'ec2-54-149-241-242',
           'ec2-54-200-220-104',
           'ec2-54-186-71-154',
           'ec2-54-187-60-112',
           'ec2-54-191-34-208',
           'ec2-54-186-51-184',
           'ec2-54-191-22-46',
           'ec2-54-187-44-98',
           'ec2-54-191-202-134',
           'ec2-54-186-127-159',
           'ec2-54-186-7-149',
           'ec2-54-186-3-60',
           'ec2-54-186-60-214',
           'ec2-54-191-254-248',
           'ec2-54-186-72-118',
           'ec2-54-149-239-52']


def create_ec2_scp(fp, servers):
    with open(fp, 'w') as o:
        for server in servers:
            o.write('scp -i ~/Dropbox/AWS/cchen224-or.pem '
                    'ec2-user@' + server + '.us-west-2.compute.amazonaws.com:*.csv '
                    '~/Downloads/u/\n')

