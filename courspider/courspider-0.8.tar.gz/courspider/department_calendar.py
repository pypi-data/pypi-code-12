import re

from courspider.faculty_calendar_resources.department import Department
from courspider.faculty_calendar_resources.url import URL
from courspider.course import Course

class DepartmentCalendar:

    def __init__(self, session, url):
        """
        Initialize a new Department Calendar for the given url

        :param session: The session of the calendar
        :type session: Session
        :param url: The url to the specified year's calendar
        :type url: URL
        """
        self.session = session
        self.url = url
        self.department = DepartmentCalendar.find_department_name(url)
        self.courses = []

    # regex used for the _find_department method
    _department_name = re.compile(r"<h1>(.*)<\/h1>")

    @staticmethod
    def find_department_name(url):
        """
        Return the Department found at the given url

        :param url: The url of the department.
        :type url: URL
        :return: The Department
        :rtype: Department
        """
        matches = DepartmentCalendar._department_name.\
                findall(url.raw_html)

        # only a single h1 tag in the html, and it is the department name
        return Department(matches[0])

    # please don't touch this regular expression without fully understanding it
    # it has been adjusted after many iterations after finding strange
    # formatting in the raw html, so any changes is not advised

    # regular expression used to filter out the course data
    regex = '<a name="([A-Z]{3}\\d\\d\\d[A-Z]\\d)"><\/a>'\
            '<span class="strong">\\1\\s*(.*?)<\/span>\\s*(<\/p>)?'\
            '\s*<\/?p(.*?)?>(.*?)<\/?p>\\s*(<p>)?'\
            '(\s*<p>(.*?)<\/p>)?(\s*<p>(.*?)<\/p>)?\s*(<p>)?\s*'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?'\
            '(\\s*<br>)?'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?'\
            '(\\s*<br>)?'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?'\
            '(\\s*<br>)?'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?'\
            '(\\s*<br>)?'\
            '\s*(Distribution Requirement Status:\\s*(.*?)\\s*)?(<br>)?\s*'\
            '(Breadth Requirement:\\s*(.*?)\\s*)?(<br>|<\/?p>)'

    _course = re.compile(regex, re.DOTALL)

    def get_courses(self):
        """
        Returns a list of all the courses in this Department Calendar.

        :return: list of all courses in this DepartmentCalendar
        :rtype: list[Course]
        """
        # if the list has been generated
        if self.courses:
            return self.courses

        # generate list if necessary
        courses_data = DepartmentCalendar._course.findall(self.url.raw_html)

        for course_data in courses_data:
            self.courses.append(self._create_course(course_data))

        return self.courses.copy()

    def _create_course(self, data):
        """
        Create a course object from the data extracted using the above regex

        :param data: The data extracted using the above regex
        :type data: tuple(str, ...)
        :return: A course object
        :rtype: Course
        """
        # these numbers come from the group numbers from the regex above
        # '_course' count them if you wanna
        course_code = DepartmentCalendar._erase_html(data[0])
        course_name = DepartmentCalendar._erase_html(data[1])
        course_description = DepartmentCalendar._erase_html(
            data[4] + data[7] + data[9])
        exclusion = DepartmentCalendar._erase_html(
            DepartmentCalendar._select_data(data, 12))
        prerequisite = DepartmentCalendar._erase_html(
            DepartmentCalendar._select_data(data, 13))
        corequisite = DepartmentCalendar._erase_html(
            DepartmentCalendar._select_data(data, 14))
        recommended = DepartmentCalendar._erase_html(
            DepartmentCalendar._select_data(data, 15))
        distribution_requirement = DepartmentCalendar._erase_html(
            data[36])
        breath_requirement = DepartmentCalendar._erase_html(data[39])

        print("found course: {}".format(course_code))

        return Course(course_code, course_name, course_description,
                      exclusion, prerequisite, corequisite, recommended,
                      distribution_requirement, breath_requirement,
                      self.department)

    def _select_data(data, start):
        result = ""
        for i in range(4):
            result += data[start + i * 4]
        return result

    _tags = re.compile('<.*?>', re.DOTALL)

    @staticmethod
    def _erase_html(data):
        """
        Erases any remaining html tags in the text.

        :param data: The raw data
        :type data: str
        :return: The data after removing remaining html tags
        :rtype: str
        """
        return DepartmentCalendar._tags.sub('', data)
