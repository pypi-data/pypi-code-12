class Department:

    departments = {}

    def __init__(self, name):
        """
        Represents a department

        :param name: the name of the department
        :type name: string
        """
        self.name = name

    def __str__(self):
        """
        Return a string representation of a department

        :return: string representation of a department
        :rtype: str
        """
        return self.name

    def __eq__(self, other):
        """
        Returns True if this Department is equal to other.

        They are equal if and only if other is an instance of a Department, and
        both departments have the same name

        :param other: The other object to compare to
        :type other: Object
        :return: whether or not these they are equal
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.name == other.name
        return False

    @staticmethod
    def create(name):
        """
        Returns an instance of Department with the given name.

        If a Department instance with the same name has already been created,
        it will be returned

        :return: a Department instance with the given name
        :rtype: Department
        """
        if name in departments:
            return departments[name]

        department = Department(name)
        departments[name] = department

        return department
