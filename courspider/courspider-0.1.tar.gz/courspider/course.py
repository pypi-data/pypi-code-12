class Course:

    # all of the labels for the data of a course
    labels = ['Course code', 'Course name', 'Course description',
             'Course exclusion', 'Course prerequisite',
             'Course corequisite', 'Course preparation',
             'Course distribution requirement',
             'Course breadth requirement']

    def __init__(self, course_code, course_name, course_description,
                 exclusion, prerequisite, corequisite, recommended,
                 distribution_requirement, breadth_requirement):
        """
        Represents a single Course

        :param course_code: The code of this Course
        :type course_code: str
        :param course_name: The name of this Course
        :type course_name: str
        :param course_description: The description of this Course
        :type course_description: str
        :param exclusion: The exclusions of this Course
        :type exclusion: str
        :param prerequisite: The prerequisites of this Course
        :type prerequisite: str
        :param corequisite: The corequities of this Course
        :type corequisite: str
        :param recommended: The recommended preparation of this Course
        :type recommended: str
        :param distribution_requirement: The distribution requirement of this
                                         Course
        :type distribution_requirement: str
        :param breadth_requirement: The breadth requirement of this Course
        :type breadth_requirement: str
        """
        self.course_code = Course._format(course_code)
        self.course_name = Course._format(course_name)
        self.course_description = Course._format(course_description)
        self.exclusion = Course._format(exclusion)
        self.prerequisite = Course._format(prerequisite)
        self.corequisite = Course._format(corequisite)
        self.recommended = Course._format(recommended)
        self.distribution_requirement = Course._format(distribution_requirement)
        self.breadth_requirement = Course._format(breadth_requirement)

        self.data = [self.course_code, self.course_name,
                     self.course_description, self.exclusion,
                     self.prerequisite, self.corequisite, self.recommended,
                     self.distribution_requirement, self.breadth_requirement]

    def __str__(self):
        """
        Returns a string representation of this course

        :return: A string representation of this Course
        :rtype: str
        """
        delimiter = '\n' * 2
        return delimiter.join([label + ': ' + data for label, data in \
                zip(Course.labels, self.data)])

    def to_data(self):
        """
        Return the information of a course as a set of key-value pairs in a
        dictionary.

        :return: A dictionary containing the course information as its key-value
                 pairs
        :rtype: dict{str, str}
        """
        course = {}
        for label, data in zip(Course.labels, self.data):
            course[label] = data
        return course

    @staticmethod
    def _format(val):
        """
        Used to format the values of the information and removes leading and
        trailing white space characters.

        If the value is an empty string or contains only white space characters,
        return 'None'

        :param val: The value to be formatted
        :type val: str
        :return: The formatted value
        :rtype: str
        """
        val = val.strip()
        return val if val is not "" else 'None'
