from darwinpush.messages import *
from darwinpush.messagefactories.xml import *

import logging
log = logging.getLogger("darwinpush")

class Parser:

    def __init__(self, q_in, q_out, quit):
        self.q_in = q_in
        self.q_out = q_out
        self.quit = quit

    def run(self):
        while not self.quit.is_set():
            (m, message, source) = self.q_in.get()

            # check for dummy message that signals quit
            if m is None and message is None and source is None:
                break

            self.parse(m, message, source)

    def parse(self, m, message, source):
        # We aren't ever expecting the Snapshot Record component to contain anything.
        if m.sR is not None:
            print("o.O.o.O Snapshot record is not none.")
            sys.exit(1)

        # We are expecting the Update Record to contain something though!
        if m.uR is None:
            print("o.O.o.O Update record is none.")
            sys.exit(1)

        # Make r the record we are looking at.
        r = m.uR

        # Process SCHEDULE messages.
        for i in r.schedule:
            log.debug("SCHEDULE message received.")
            o = ScheduleXMLMessageFactory.build(i, m, message)
            self.q_out.put((o, source))

        # Process DEACTIVATED messages.
        for i in r.deactivated:
            log.debug("DEACTIVATED message received.")
            o = DeactivatedMessage(i, m, message)
            self.q_out.put((o, source))

        # Process ASSOCATION messages.
        for i in r.association:
            log.debug("ASSOCIATION message received.")
            o = AssociationMessage(i, m, message)
            self.q_out.put((o, source))

        # Process TS messages.
        for i in r.TS:
            log.debug("TS message received.")
            o = TrainStatusXMLMessageFactory.build(i, m, message)
            self.q_out.put((o, source))

        # Process OW messages.
        for i in r.OW:
            log.debug("OW message received.")
            o = StationMessage(i, m, message)
            self.q_out.put((o, source))

        # Process TRAINALERT messages.
        for i in r.trainAlert:
            log.debug("TRAINALERT message received.")
            o = TrainAlertMessage(i, m, message)
            self.q_out.put((o, source))

        # Process TRAINORDER messages.
        for i in r.trainOrder:
            log.debug("TRAINORDER message received.")
            o = TrainOrderMessage(i, m, message)
            self.q_out.put((o, source))

        # Process TRACKINGID messages.
        for i in r.trackingID:
            log.debug("TRACKINGID message received.")
            o = TrackingIdMessage(i, m, message)
            self.q_out.put((o, source))

        # Process ALARM messages.
        for i in r.alarm:
            log.debug("ALARM message received.")
            o = AlarmMessage(i, m, message)
            self.q_out.put((o, source))
