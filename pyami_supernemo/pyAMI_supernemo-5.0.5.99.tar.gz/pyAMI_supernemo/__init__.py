#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#           jerome.odier@lpsc.in2p3.fr
#
# Version : 1.X.X for pyAMI_supernemo (2013-2014)
#
#############################################################################

import pyAMI.config, pyAMI_supernemo.config

#############################################################################

pyAMI.config.version = pyAMI_supernemo.config.version

pyAMI.config.bug_report = pyAMI_supernemo.config.bug_report

#############################################################################

pyAMI.config.endpoint_descrs['supernemo'] = {'prot': 'https', 'host': 'ami-supernemo.in2p3.fr', 'port': '443', 'path': '/AMI/servlet/net.hep.atlas.Database.Bookkeeping.AMI.Servlet.Command'}

#############################################################################
