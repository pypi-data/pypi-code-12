"""
Sync DFP API Services => Amazon S3 As AVRO
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from traceback import format_exc 

from dfp_sync.common import DFPService
from dfp_sync.utils import threaded
from dfp_sync.utils import write_avro_to_s3
from dfp_sync.utils import write_to_s3


def setup(parser):
  """
  Arguments for the service command.
  """
  srv_parser = parser.add_parser("service", 
    help="Sync Doubleclick API Service Data.")

  srv_parser.add_argument('service_name', type=str, default=None,
    help='The service name to sync.', choices=DFPService.SERVICES + ["All"])

  srv_parser.add_argument('-c', '--config', type=str, default='googleads.yaml',
    help='The path to your googleads.yaml file.')

  srv_parser.add_argument('-n', '--chunk-size', type=int, 
    help='The number of records to dump per file', default=15000)

  srv_parser.add_argument('-w', '--where', type=str, default=None,
    help='Optional PQL filter statement to apply to a service. Ignored when service_name == "All"')

  srv_parser.add_argument('-o', '--offset', 
    help='Optional PQL offset to apply', type=int, default=0)

  srv_parser.add_argument('--log-every', type=int, default=1000,
    help='How often to log process (in number of records).')

  srv_parser.add_argument('-d', '--s3-data-dir', type=str, 
    help='The S3 Bucket where the files should be stored.')

  srv_parser.add_argument('-s' , '--s3-schema-path', type=str, 
    help='The S3 Bucket where the files should be stored.')

  srv_parser.add_argument('-g' , '--generate', action="store_true",
    help='Generate commands to import all data in chunked execution.')

  return 'service', run


def run(opts):
  if opts.generate:
    gen_export_commands(opts)
    return
  return export_service(opts)

def gen_export_commands(opts):
  """
  Generate a list of commands to export all data in parallel.
  """

  # connect to client + service + schmema
  service = DFPService(opts.service_name, config=opts.config)
  total_records = service.get_n_records()
  for offset in range(0, total_records or 1, opts.chunk_size):
    print("{7} service {0} -o {1} -n {2} -d {3} -s {4} -c {5} --log-every {6}"
          .format(opts.service_name, 
                  offset, 
                  opts.chunk_size, 
                  opts.s3_data_dir, 
                  opts.s3_schema_path, 
                  opts.config,
                  opts.log_every,
                  sys.argv[0]))

def export_service(opts):
  """
  Transfer All Records from a DFP service 
  to avrofiles on S3.
  """
  print('INFO: Exporting {0}'.format(opts.service_name))
  
  # connect to client + service + schmema
  service = DFPService(opts.service_name, config=opts.config)

  # export all records from service and 
  # write chunks of avro to s3.
  n_records = 0
  part = 1
  records = []

  for record in service.get_records(where=opts.where, limit=opts.chunk_size, offset=opts.offset):

    # increment record counter
    n_records += 1
    records.append(record)
    
    # log record count for service.
    if n_records % opts.log_every == 0:
      print('INFO: Processed records {0} to {1} for {2}'\
            .format(opts.offset + (opts.log_every * (part-1)), 
                    n_records + opts.offset,
                    opts.service_name))
      part += 1

  # write remaining records to s3.
  if len(records):
    
    fp = '%s/%d-%d.avro' % (opts.s3_data_dir, opts.offset, opts.offset + opts.chunk_size)
    print("INFO: Dumping {0} records to {1}".format(n_records, fp))
    write_avro_to_s3(fp, 
                     records, 
                     service.schema.to('avro'),
                     key=opts.aws_key,
                     secret=opts.aws_secret)

  # write schema for created tables.
  if n_records > 0:

    print("INFO: Writing schema to {0}".format(opts.s3_schema_path))
    write_to_s3(opts.s3_schema_path, 
                service.schema.to('avsc'),
                key=opts.aws_key,
                secret=opts.aws_secret)


