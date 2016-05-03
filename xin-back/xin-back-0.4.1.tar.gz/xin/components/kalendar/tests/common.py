from ..model.calendar_model import Calendar
from ..model.meeting import Meeting


class BaseTest:

    @classmethod
    def clean_db(cls):
        Calendar.collection.drop()
        Meeting.collection.drop()
