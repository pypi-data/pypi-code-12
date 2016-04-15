from darwinpush.messages import *

class Listener:
    def __init__(self, q, quit):
        print("Initialising Listener")
        self.queue = q
        self.quit = quit

    def _run(self):
        print("Running listener")

        while not self.quit.is_set():
            (message, source) = self.queue.get()

            # dummy message that signals quit
            if message is None and source is None:
                break

            self.route_message(message, source)

    def route_message(self, message, source):
        if type(message) == ScheduleMessage:
            self.on_schedule_message(message, source)
        elif type(message) == DeactivatedMessage:
            self.on_deactivated_message(message, source)
        elif type(message) == AssociationMessage:
            self.on_association_message(message, source)
        elif type(message) == TrainStatusMessage:
            self.on_train_status_message(message, source)
        elif type(message) == StationMessage:
            self.on_station_message(message, source)
        elif type(message) == TrainAlertMessage:
            self.on_train_alert_message(message, source)
        elif type(message) == TrainOrderMessage:
            self.on_train_order_message(message, source)
        elif type(message) == TrackingIdMessage:
            self.on_tracking_id_message(message, source)
        elif type(message) == AlarmMessage:
            self.on_alarm_message(message, source)
        else:
            print("Another type of message")

    def on_schedule_message(self, message, source):
        pass

    def on_deactivated_message(self, message, source):
        pass

    def on_association_message(self, message, source):
        pass

    def on_train_status_message(self, message, source):
        pass

    def on_station_message(self, message, source):
        pass

    def on_train_alert_message(self, message, source):
        pass

    def on_train_order_message(self, message, source):
        pass

    def on_tracking_id_message(self, message, source):
        pass

    def on_alarm_message(self, message, source):
        pass
