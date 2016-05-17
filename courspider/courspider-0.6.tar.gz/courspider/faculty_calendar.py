import re

from courspider.raw_html import get_html


class FacultyCalendar:
    """
    Represents an instance of a particular faculty calendar for a certain year.
    """

    def __init__(self, faculty, session, url):
        """
        Initialize a new Faculty Calendar for the given url

        :param faculty: The faculty the calendar belongs to
        :type faculty: Faculty
        :param session: The session of the calendar
        :type session: Session
        :param url: The url to the specified year's calendar
        :type url: URL
        """
        self.faculty = faculty
        self.session = session
        self.url = url
        self.department_calendars = []

    def get_department_calendars(self):
        """
        Return a list of Department Calendar from this year of this Faculty
        """
        if self.department_calendars:
            return self.department_calendars
        else:
            return self._generate_department_calendars_from_html()

    def _generate_department_calendars_from_html(self):
        """
        Using the unescaped raw html of the calendar, create and return all the
        department calendars found.
        """
        raise NotImplementedError
