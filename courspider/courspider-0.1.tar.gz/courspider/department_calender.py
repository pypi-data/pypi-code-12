import re

from faculty_calender_resources.department import Department
from course import Course

class DepartmentCalender:

    def __init__(self, session, url):
        """
        Initialize a new Department Calender for the given url

        :param session: The session of the calender
        :type session: Session
        :param url: The url to the specified year's calender
        :type url: URL
        """
        self.session = session
        self.url = url
        self.department = self._find_department()
        self.courses = []

    # regex used for the _find_department method
    _department_name = re.compile(r"<h1>(.*)<\/h1>")

    def _find_department(self):
        """
        Return the Department found at the given url

        :return: The Department
        :rtype: Department
        """
        matches = DepartmentCalender._department_name.\
                findall(self.url.raw_html)

        # only a single h1 tag in the html, and it is the department name
        return Department(matches[0])

    # please don't touch this regular expression without fully understanding it
    # it has been adjusted after many iterations after finding strange
    # formatting in the raw html, so any changes is not advised

    # regular expression used to filter out the course data
    regex = '<a name="([A-Z]{3}\\d\\d\\d[A-Z]\\d)"><\/a>'\
            '<span class="strong">\\1\\s*(.*?)<\/span>\\s*'\
            '<\/?p(.*?)?>([\\s\\S]*?)<\/?p>\\s*'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?(<br>)?'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?(<br>)?'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?(<br>)?'\
            '(Exclusion:\\s*(.*?)|Prerequisite:\\s*(.*?)|'\
            'Corequisite:\\s*(.*?)|Recommended Preparation:\\s*(.*?))?(<br>)?'\
            '(Distribution Requirement Status:\\s*(.*?)\\s*)?(<br>)?'\
            '(Breadth Requirement:\\s*(.*?)\\s*)?<br>'

    _course = re.compile(regex, re.DOTALL)

    def get_courses(self):
        """
        Returns a list of all the courses in this Department Calender.

        :return: list of all courses in this DepartmentCalender
        :rtype: list[Course]
        """
        # if the list has been generated
        if self.courses:
            return self.courses

        # generate list if necessary
        courses_data = DepartmentCalender._course.findall(self.url.raw_html)

        for course_data in courses_data:
            self.courses.append(DepartmentCalender._create_course(course_data))

        return self.courses.copy()

    @staticmethod
    def _create_course(data):
        """
        Create a course object from the data extracted using the above regex

        :param data: The data extracted using the above regex
        :type data: tuple(str, ...)
        :return: A course object
        :rtype: Course
        """
        # these numbers come from the group numbers from the regex above
        # '_course' count them if you wanna
        course_code = DepartmentCalender._erase_html(data[0])
        course_name = DepartmentCalender._erase_html(data[1])
        course_description = DepartmentCalender._erase_html(data[3])
        exclusion = DepartmentCalender._erase_html(
            data[5] + data[11] + data[17] + data[23])
        prerequisite = DepartmentCalender._erase_html(
            data[6] + data[12] + data[18] + data[24])
        corequisite = DepartmentCalender._erase_html(
            data[7] + data[13] + data[19] + data[25])
        recommended = DepartmentCalender._erase_html(
            data[8] + data[14] + data[20] + data[26])
        distribution_requirement = DepartmentCalender._erase_html(
            data[29])
        breath_requirement = DepartmentCalender._erase_html(data[32])

        print("found course: {}".format(course_code))

        return Course(course_code, course_name, course_description,
                      exclusion, prerequisite, corequisite, recommended,
                      distribution_requirement, breath_requirement)

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
        return DepartmentCalender._tags.sub('', data)
