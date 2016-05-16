from sdk import *
import time

TEST_DEBUG_URL_PREFIX = 'http://cloud_test.cloud.sensorsdata.cn:8006/sa?token=89575628ca400c7b' 

consumer = DebugConsumer(TEST_DEBUG_URL_PREFIX, True)
sa = SensorsAnalytics(consumer)
sa.register_super_properties({'$app_version' : '1.0.1', 'hahah' : 123})

def inFunction():
    sa.track(1234, 'Test', {})

class XXX:

    def inClass(self):
        sa.track(1234, 'Test', {})


p = {'$time' : int(time.time() * 1000), 'aaa' : 123}
print(p)
sa.track(1234, 'Test', p)
print(p)
sa.track(1234, 'Test', p)
print(p)

inFunction()

XXX().inClass()
