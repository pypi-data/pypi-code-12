import argparse
import sys
from s3 import downloadfile,uploadfile,multiparts,bucket
from ec2 import instance,vpc,subnet,route,security

def parse_s3_group_args(parser,group):
    
    group.add_argument("-upload", "--upload", action='store_true', dest="is_upload_command",help='set the param is upload file to bucket in s3 group',default=False)
    group.add_argument("-download", "--download", action='store_true', dest="is_download_command",help='set the param is download file in bucket to local computer in s3 group',default=False)
    group.add_argument("-bucket", "--bucket", action='store_true', dest="is_bucket_command",help='set the param is about bucket commands and operations in s3 group',default=False)
    group.add_argument("-multiparts", "--multiparts", action='store_true', dest="is_multipart_command",help='set the param is about the multipart command and operations',default=False)

    args = parser.parse_args(sys.argv[2:3])
    prog = sys.argv[0]
    sys.argv = sys.argv[3:]
    sys.argv.insert(0,prog)
    if args.is_download_command:
        downloadfile.main()
    elif args.is_upload_command:
        uploadfile.main()
    elif args.is_multipart_command: 
        multiparts.main()
    elif args.is_bucket_command:
        bucket.main()
    else:
        parser.print_help()

def parse_ec2_group_args(parser,group):

    group.add_argument("-instance", "--instance", action='store_true', dest="is_create_instance",help='set the param is create instance in ec2 group',default=False)
    group.add_argument("-vpc", "--vpc", action='store_true', dest="is_create_vpc",help='set the param is create vpc in ec2 group',default=False)
    group.add_argument("-subnet", "--subnet", action='store_true', dest="is_create_subnet",help='set the param is create subnet in ec2 group',default=False)
    group.add_argument("-route", "--route", action='store_true', dest="is_create_route",help='set the param is create route in ec2 group',default=False)
    group.add_argument("-security", "--security", action='store_true', dest="is_create_security",help='set the param is create security group in ec2 group',default=False)
    
    args = parser.parse_args(sys.argv[2:3])
    prog = sys.argv[0]
    sys.argv = sys.argv[3:]
    sys.argv.insert(0,prog)
    if args.is_create_instance:
        instance.main()
    elif args.is_create_subnet:
        subnet.main()
    elif args.is_create_vpc:
        vpc.main()
    elif args.is_create_route:
        route.main()
    elif args.is_create_security:
        security.main()
    else:
        parser.print_help()
   
def main():
    
    parser = argparse.ArgumentParser()

    s3_group = parser.add_argument_group("-s3",'s3 param groups')
    s3_group.add_argument("-s3", "--s3", action='store_true', dest="is_s3_group",help='set the param is s3 storage group params true or false',default=False)

    ec2_group = parser.add_argument_group("-ec2",'ec2 param groups')
    ec2_group.add_argument("-ec2", "--ec2", action='store_true', dest="is_ec2_group",help='set the param is ec2 group params true or false',default=False)
    
    if 1 == len(sys.argv):
        parser.print_help()
        sys.exit(0)
    args = parser.parse_args(sys.argv[1:2])

    if args.is_s3_group:
        parse_s3_group_args(parser,s3_group)
    elif args.is_ec2_group:
        parse_ec2_group_args(parser,ec2_group)

if __name__ == "__main__":
    main()
    
