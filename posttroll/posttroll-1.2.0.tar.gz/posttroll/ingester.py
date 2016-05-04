#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Ingest messages
"""



from posttroll.publisher import Publish
from posttroll.message import Message
import time
import os.path


files = ["/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1201518_e1202274_b00001_c20130228154745886000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1202292_e1203528_b00001_c20130228154905253000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1203546_e1205182_b00001_c20130228155026403000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1205200_e1206436_b00001_c20130228155147398000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1206454_e1208090_b00001_c20130228155309492000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1208108_e1209344_b00001_c20130228155436507000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1209362_e1210598_b00001_c20130228155605328000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1211016_e1212253_b00001_c20130228155735334000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1212270_e1213507_b00001_c20130228155828256000_nfts_drl.h5",
         "/san1/NPP/lvl0/RNSCA-RVIRS_npp_d20130214_t1213524_e1214423_b00001_c20130228155828484000_nfts_drl.h5"]


# message = 'pytroll://oper/polar/direct_readout/norrköping file safusr.u@lxserv248.smhi.se 2013-04-23T01:13:11.979056 v1.01 application/json {"satellite": "NPP", "format": "RDR", "start_time": "2013-04-23T00:55:23", "level": "0", "orbit_number": 7699, "uri": "ssh://nimbus/archive/npp/RNSCA-RVIRS_npp_d20130423_t0055217_e0110433_b00001_c20130423011303651000_nfts_drl.h5", "filename": "RNSCA-RVIRS_npp_d20130423_t0055217_e0110433_b00001_c20130423011303651000_nfts_drl.h5", "instrument": "viirs", "end_time": "2013-04-23T01:10:53", "type": "HDF5"}'

def get_rdr_times(filename):
    from datetime import datetime, timedelta

    bname = os.path.basename(filename)
    sll = bname.split('_')
    start_time = datetime.strptime(sll[2] + sll[3][:-1], 
                                   "d%Y%m%dt%H%M%S")
    end_time = datetime.strptime(sll[2] + sll[4][:-1], 
                                 "d%Y%m%dt%H%M%S")
    if end_time < start_time:
        end_time += timedelta(days=1)
    return start_time, end_time

def create_rdr_message(filename):

    data = {}
    data["satellite"] = "NPP"
    data["format"] = "RDR"
    data["instrument"] = "viirs"
    data["type"] = "HDF5"
    data["level"] = "0"
    data["orbit_number"] = "00001"
    
    data["start_time"], data["end_time"] = get_rdr_times(filename)
    data["filename"] = os.path.basename(filename)
    data["uri"] = "ssh://safe.smhi.se" + filename
    
    return Message("/oper/polar/direct_readout/norrköping", "file", data)

try:
    with Publish("ingester", ["RDR"], 9042) as pub:
        for filename in files:
            message = create_rdr_message(filename)
            print "publishing", message
            pub.send(str(message))
            time.sleep(3)
except KeyboardInterrupt:
    print "terminating publisher..."
