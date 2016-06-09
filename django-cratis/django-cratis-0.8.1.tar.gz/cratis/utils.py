from abc import ABC, abstractmethod


class Resolvable(ABC):

    @abstractmethod
    def resolve(self):
        """
        Returns set of resolved values
        """


class Collectable(Resolvable):

    def __init__(self, unique=True, _format=tuple):
        self.val = ()
        self.unique = unique
        self._format = _format

    def append(self, vals):
        if isinstance(vals, str):
            vals = (vals,)

        for val in vals:
            if not self.unique or (val not in self.val):
                self.val += (val,)

    def resolve(self):
        return self._format(self.val)
