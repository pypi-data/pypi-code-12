"""Definition of a user representation"""


from pyrosalind import parser


class User:
    """User data holder, and wrapper around the parser API
    to get user data from username on ROSALIND

    """

    def __init__(self, name:str, solved_problems:iter):
        self._name = name
        self._solved = set(solved_problems)
        # self._badges = set()  # TODO
        # self._achievements = set()  # TODO


    @property
    def name(self): return self._name

    @property
    def solved(self): return self._solved

    @property
    def badges(self): return self._badges


    @staticmethod
    def from_name(name):
        """Parse ROSALIND directly to get all informations necessary"""
        return User(name, (problem for problem in parser.problems(name)))


    def __str__(self):
        return self.name + ' (' + str(len(self.solved)) + ' problems solved)'
