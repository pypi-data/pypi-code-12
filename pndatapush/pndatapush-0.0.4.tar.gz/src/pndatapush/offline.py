import urllib2
import os
import logging
from threading import Thread
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sensordata import SensorData, Base, SensorDataPushState
from utils import get_or_create
from pushdata import PushDataBase

DEFAULT_DB_PATH = 'sqlite:///%s/sensordata.db' % os.path.dirname(os.path.realpath(__file__))
DEFAULT_IP_ADDRESS = '85.91.7.19'  # 85.91.7.19 is one of the IP-addresses for google.ie


def active_internet_connection(ipaddress = DEFAULT_IP_ADDRESS):
    try:
        response = urllib2.urlopen('http://%s' % ipaddress, timeout=1)
        return True
    except urllib2.URLError as url_err:
        pass  # there was a urllib2 exception - we don't really care why as we know that we don't have internet access
    except Exception as unknown_error:
        pass  # there was an unknown exception - we don't really care why as we know that we don't have internet access
    return False


class Offline(object):
    session = null
    engine = null
    payload_consumers = []
    dbpath = null
    ipaddress = null

    def __init__(self, payload_consumers=[], dbpath=DEFAULT_DB_PATH, ipaddress=DEFAULT_IP_ADDRESS):
        self.dbpath = dbpath
        self.payload_consumers = payload_consumers
        self.ipaddress = ipaddress

        self.engine = create_engine(self.dbpath,
                                    echo=False)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.createdb()  # Create the database if it doesn't exist

        # start a thread that loops through all unsent messages and pushes to all configured consumers
        self.start_push_thread()

    def save(self, deviceid, payload):
        payloadobj = SensorData(deviceid=str(deviceid), timestamp=str(datetime.utcnow()), payload=str(payload))
        self.session.add(payloadobj)
        self.session.commit()

    def get_dbath(self):
        return self.dbpath

    def createdb(self):
        # Create the database if it doesn't exist
        Base.metadata.create_all(self.engine, checkfirst=True)

    def start_push_thread(self):
        thread = Thread(target=self.push_unsent_payloads)
        thread.daemon = True
        thread.start()

    def push_unsent_payloads(self):
        # we need to create our own session here as we're running in a new thread
        local_session = self.Session()
        while True:  # Infinite loop while parent process is working
            # check if internet access
            if active_internet_connection(self.ipaddress):

                unsent_sensordata = local_session.query(SensorData).filter_by(sent=False)

                for sensordata in unsent_sensordata:
                    for consumer in self.payload_consumers:
                        if not isinstance(consumer, PushDataBase):
                            consumer_obj = consumer()
                        else:
                            consumer_obj = consumer

                        # get SensorDataPushState entry for this payload. If it doesn't exist. Create it
                        consumer_push_state, created = get_or_create(local_session, SensorDataPushState,
                                                                     defaults={'timestamp': str(datetime.utcnow()),
                                                                               'attempts': 0,
                                                                               'aborted': False},
                                                                     sensordata_id=sensordata.id,
                                                                     consumer=str(consumer_obj.name))
                        # check to see if has been sent already. it's it's just been created then the answer is no
                        if created or (not consumer_push_state.aborted and not consumer_push_state.sent):
                            # we need to check that it was successful.
                            push_success = consumer_obj.push(sensordata)

                            consumer_push_state.attempts += 1  # add one to the number of attempts
                            consumer_push_state.timestamp = str(datetime.utcnow())

                            if push_success:
                                consumer_push_state.sent = True
                            else:
                                if consumer_push_state.attempts > consumer_obj.max_retries:
                                    logging.error('%s push aborted after too many retries' % consumer_push_state)
                                    consumer_push_state.aborted = True

                            # check to see if there are any more consumers of this data left to push.
                            # if not then we can now mark it as sent
                            unsent_count = local_session.query(func.count(SensorDataPushState.id))\
                                .filter_by(sensordata_id=sensordata.id,
                                           sent=False,
                                           aborted=False).scalar()
                            if unsent_count == 0:
                                sensordata.sent = True

                        local_session.commit()

