from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SensorDataPushState(Base):
    __tablename__ = 'sensordatapushstate'

    id = Column(Integer, Sequence('data_id_seq'), primary_key=True)
    timestamp = Column(Text, nullable=False)
    consumer = Column(String, index=True, nullable=False)
    sent = Column(Boolean, index=True, default=False)
    attempts = Column(Integer, nullable=False, default=0)

    # If too many attempts have been made then it will abort trying to send
    aborted = Column(Boolean, index=True, default=False)

    sensordata_id = Column(Integer, ForeignKey('sensordata.id'))
    sensordata = relationship("SensorData", back_populates="consumers")

    def __repr__(self):
        return "<SensorDataPushState(id='%d', deviceid='%s', timestamp='%s', consumer='%s', sent='%s')>" % (
            self.id, self.sensordata.deviceid, self.timestamp, self.consumer, self.sent)

class SensorData(Base):
    __tablename__ = 'sensordata'

    id = Column(Integer, Sequence('data_id_seq'), primary_key=True)
    timestamp = Column(Text, nullable=False)
    deviceid = Column(String, index=True, nullable=False)
    payload = Column(String, nullable=False)

    sent = Column(Boolean, index=True, default=False)

    consumers = relationship("SensorDataPushState", order_by=SensorDataPushState.id, back_populates="sensordata")

    def __repr__(self):
        return "<SensorData(id='%d', deviceid='%s', timestamp='%s', payload='%s', sent='%s')>" % (
            self.id, self.deviceid, self.timestamp, self.payload, self.sent)

