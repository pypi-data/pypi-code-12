from sensordata import SensorData
from pushdata import PNPushData
from offline import Offline

offline = Offline(payload_consumers=[PNPushData])
offline.save('12456', 30.00)
offline.save('22456', 42)
offline.save('32456', 57)

for row in offline.session.query(SensorData).all():
    print('[%s] %s : %s') % (str(row.deviceid), str(row.timestamp), str(row.payload))
