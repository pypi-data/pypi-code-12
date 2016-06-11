from enum import Enum


class Session:

    def __init__(self, year, season):
        """
        Represents a school year.

        :param year: the year the session started in
        :type year: int
        :param season: the season the session started in
        :type season: Season
        """
        self.year = year
        self.season = season

    def __str__(self):
        """
        Return a string representation of a Session

        :return: string representation of a Session
        :rtype: str
        """
        return str(self.year) + str(self.season)

    def __eq__(self, other):
        """
        Returns True if this Session is equal to other.

        They are equal if and only if other is an instance of a Session, and
        both sessions have the same year and season

        :param other: The other object to compare to
        :type other: Object
        :return: whether or not these they are equal
        :rtype: bool
        """
        if isinstance(other, self.__class__):
            return self.year == other.year and self.season == other.season
        return False

class Season(Enum):
    FALL = 0
    SUMMER = 1
