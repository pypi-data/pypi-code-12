#!/usr/bin/env python

import xbob.db.faceverif_fl

# 0/ The database to use
name = 'mobile0-gender'
db = xbob.db.faceverif_fl.Database('/idiap/user/ekhoury/LOBI/work/spkRecTool_2013_01_10/databases/mobio2_protocols/mobile0-gender_recognition/case1/face/')
protocol = 'mobile0-gender'

img_input_dir = "/idiap/temp/lelshafey/gender_mobio/gender_noexternal/features/" # not really used 
img_input_ext = ".wav"

