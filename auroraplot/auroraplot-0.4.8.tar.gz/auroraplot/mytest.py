#!/usr/bin/python

import time
t1 = time.time()

import numpy as np
import matplotlib as mpl
import auroraplot as ap
import samnet
import aurorawatchnet


from matplotlib import pyplot as plt

plt.close('all')



ap.add_network('SAMNET', samnet.sites)
ap.add_network('AURORAWATCHNET', aurorawatchnet.sites)

st=np.datetime64('2012-01-01T00:00:00Z')
et=np.datetime64('2012-01-04T12:00:00Z')
day = np.timedelta64(1, 'D').astype('m8[us]')

switch = 4
if switch == 0:
    q=ap.load_data('SAMNET','LAN','MagData',st,et,archive='realtime')
elif switch == 1:
    q=ap.load_data('SAMNET','LAN','MagData',st,et, 
                    path='file:/data/samnet/realtime/lan/2012/01/lan%Y%m%d.rt',
                    archive='realtime')
elif switch == 2:
    st = np.datetime64('2013-01-01T00:00:00Z')
    et = np.datetime64('2013-01-04T12:00:00Z')

    q = ap.load_data('AURORAWATCHNET', 'LAN1', 'MagData', st, et)
    # q=ap.load_data('SAMNET', 'LAN', 'MagData', st, et)

elif switch == 3:
    st = np.datetime64('2013-01-01T00:00:00Z')
    et = np.datetime64('2013-01-04T12:00:00Z')
    q = ap.load_data('AURORAWATCHNET', 'LAN1', 
                      'TemperatureData', st, et)


elif switch == 4:
    st = np.datetime64('2013-01-01T00:00:00Z')
    et = np.datetime64('2013-01-04T12:00:00Z')

    q = ap.load_data('AURORAWATCHNET', 'LAN1', 'MagData', st, et)
    sam = ap.load_data('SAMNET', 'LAN', 'MagData', st, st+day,
                       archive='realtime')
    #z = ap.load_data('AURORAWATCHNET', 'LAN1', 
    #                  'TemperatureData', st, et)
    #v = ap.load_data('AURORAWATCHNET', 'LAN1', 
    #                  'VoltageData', st, et)

elif switch == 5:
    st = np.datetime64('2013-01-01T00:00:00Z')
    et = np.datetime64('2013-09-08T18:00:00Z')

    q = ap.load_data('AURORAWATCHNET', 'LAN1', 'MagData', st, et)
    # q=ap.load_data('SAMNET', 'LAN', 'MagData', st, et)
    z = ap.load_data('AURORAWATCHNET', 'LAN1', 'TemperatureData', 
                      st, et)
    v = ap.load_data('AURORAWATCHNET', 'LAN1', 
                      'VoltageData', st, et)



    
q.plot()
plt.show()

t2 = time.time()
print('Time taken: ' + str(t2 - t1) + 's')
