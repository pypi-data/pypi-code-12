"""
List all services.
"""
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from dfp_sync.common import DFPService

def setup(parser):
  """
  Arguments for the service command.
  """
  srv_parser = parser.add_parser("ls-service", 
    help="Sync Doubleclick API Service Data.")

  return 'ls-service', run

def run(opts):
  print("\n".join(DFPService.SERVICES))