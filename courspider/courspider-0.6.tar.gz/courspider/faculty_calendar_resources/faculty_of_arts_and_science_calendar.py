import re

from bs4 import BeautifulSoup

from courspider.faculty_calendar import FacultyCalendar
from courspider.faculty_calendar_resources.department import Department
from courspider.faculty_calendar_resources.faculty import Faculty
from courspider.faculty_calendar_resources.url import URL
from courspider.department_calendar import DepartmentCalendar


class FacultyOfArtsAndScienceCalendar(FacultyCalendar):

    def __init__(self, session, url):
        """
        Represents the calendar of the Faculty of Arts and Science

        :param session: The session of the calendar
        :type session: Session
        :param url: The url to the specified year's calendar
        :type url: URL
        :return: A FacultyCalendar object for the given url
        :rtype: FacultyCalendar
        """
        super().__init__(Faculty.ARTS_AND_SCIENCE, session, url)
        self.soup = BeautifulSoup(url.raw_html, "html.parser")

    def _generate_department_calendars_from_html(self):
        """
        Using the unescaped raw html of the calendar, create and return all the
        department calendars found.

        :return: list of Department Calendar objects generated from this Faculty
                 Calendar
        :rtype: list[DepartmentCalendar]
        """

        dpeartment_calendars = []
        department_urls = []

        # generates a list of all the url endings found
        print("finding all url endings to department calendars")
        for a_tag in self.soup.find_all('a'):
            url = a_tag['href']

            if FacultyOfArtsAndScienceCalendar.\
                    _match_department_calendar_url(url):
                print("found url endings to department calendar at {}".format(url))
                department_urls.append(url)

        print("removing duplicate department url")
        # eliminate duplicate urls
        department_urls = set(department_urls)

        # generates a list of department calendars from the list of url endings
        for department_url in department_urls:
            print("converting {} to full url".format(department_url))
            url = self._to_full_url(department_url)
            calendar = DepartmentCalendar(self.session, url)
            self.department_calendars.append(calendar)

        return self.department_calendars.copy()

    def _to_full_url(self, url):
        """
        Return the full url for the link by concatenating the url ending to the
        Faculty Calendar url

        :parm url: The ending the the Department Calendar url
        :type url: str
        :return: The url to the Department Calendar
        :rtype: URL
        """
        return URL(self.url.url + '/' + url)

    # regex used for the _match_department_calendar_url method
    _department_calendar_url = re.compile(r"crs_\w\w\w.htm")

    @staticmethod
    def _match_department_calendar_url(url):
        """ Return True if the url matches what is expected of a department
        calendar url

        :param url: a possible department calendar url
        :type url:  str
        :return: True if it matches a department calendar url
        :rtype: bool
        """
        return FacultyOfArtsAndScienceCalendar.\
            _department_calendar_url.fullmatch(url) is not None
