import re

from courspider.raw_html import get_html


class FacultyCalender:
    """
    Represents an instance of a particular faculty calender for a certain year.
    """

    def __init__(self, faculty, session, url):
        """
        Initialize a new Faculty Calender for the given url

        :param faculty: The faculty the calender belongs to
        :type faculty: Faculty
        :param session: The session of the calender
        :type session: Session
        :param url: The url to the specified year's calender
        :type url: URL
        """
        self.faculty = faculty
        self.session = session
        self.url = url
        self.department_calenders = []

    def get_department_calenders(self):
        """
        Return a list of Department Calender from this year of this Faculty
        """
        if self.department_calenders:
            return self.department_calenders
        else:
            return self._generate_department_calenders_from_html()

    def _generate_department_calenders_from_html(self):
        """
        Using the unescaped raw html of the calender, create and return all the
        department calenders found.
        """
        raise NotImplementedError
