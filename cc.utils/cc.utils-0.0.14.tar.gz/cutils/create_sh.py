

servers = ['ec2-54-186-73-209',
           'ec2-54-187-85-225',
           'ec2-54-201-44-235',
           'ec2-54-201-98-138',
           'ec2-54-201-195-32',
           'ec2-54-201-231-214',
           'ec2-54-201-248-108',
           'ec2-54-201-194-137',
           'ec2-54-201-96-189',
           'ec2-54-200-70-158',
           'ec2-54-213-7-24',
           'ec2-54-201-238-175',
           'ec2-54-200-6-192',
           'ec2-54-191-13-189',
           'ec2-54-187-245-241',
           'ec2-54-191-104-153',
           'ec2-54-201-91-153',
           'ec2-54-201-67-210',
           'ec2-54-186-126-229',
           'ec2-54-201-97-151']


def create_ec2_scp(fp, servers):
    with open(fp, 'w') as o:
        for server in servers:
            o.write('scp -i ~/Dropbox/AWS/cchen224-or.pem '
                    'ec2-user@' + server + '.us-west-2.compute.amazonaws.com:*.csv '
                    '~/Downloads/u/\n')

def create_ec2_ssh(fp, servers):
    with open(fp, 'w') as o:
        for server in servers:
            o.write('ssh -i ~/Dropbox/AWS/cchen224-or.pem '
                    'ec2-user@' + server + '.us-west-2.compute.amazonaws.com\n')