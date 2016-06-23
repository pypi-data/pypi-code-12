class Integer(int):
    counts = {'add': 0, 'sub': 0,
              'mul': 0, 'div': 0,
              'lt': 0, 'gt': 0,
              'le': 0, 'ge': 0,
              'eq': 0, 'ne': 0}

    @classmethod
    def reset_counts(cls):
        for key in cls.counts.keys():
            cls.counts[key] = 0

    @classmethod
    def operations(cls):
        return sum(cls.counts[key] for key in cls.counts.keys())

    @classmethod
    def additions(cls):
        return cls.counts['add']

    @classmethod
    def subtractions(cls):
        return cls.counts['sub']

    @classmethod
    def multiplications(cls):
        return cls.counts['mul']

    @classmethod
    def divisions(cls):
        return cls.counts['div']

    @classmethod
    def comparisons(cls):
        return cls.counts['lt'] + cls.counts['gt'] + \
            cls.counts['le'] + cls.counts['ge'] + \
            cls.counts['eq'] + cls.counts['ne']

    # Constructor and representations
    def __init__(self, value):
        self.value = int(value)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __str__(self):
        return str(self.value)

    # Arithmetic operations
    def __add__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['add'] += 1
            return self.__class__(self.value + other.value)
        elif isinstance(other, int):
            self.__class__.counts['add'] += 1
            return self.__class__(self.value + other)
        else:
            raise TypeError('unsupported operand type(s) for +: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __sub__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['sub'] += 1
            return self.__class__(self.value - other.value)
        elif isinstance(other, int):
            self.__class__.counts['sub'] += 1
            return self.__class__(self.value - other)
        else:
            raise TypeError('unsupported operand type(s) for -: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __mul__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['mul'] += 1
            return self.__class__(self.value * other.value)
        elif isinstance(other, int):
            self.__class__.counts['mul'] += 1
            return self.__class__(self.value * other)
        else:
            raise TypeError('unsupported operand type(s) for -: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __div__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['div'] += 1
            return self.__class__(self.value / other.value)
        elif isinstance(other, int):
            self.__class__.counts['div'] += 1
            return self.__class__(self.value / other)
        else:
            raise TypeError('unsupported operand type(s) for -: '
                            '{} and {}'.format(self.__class__, type(other)))

    # Arithmetic operations against self
    def __iadd__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['add'] += 1
            self.value += other.value
            return self
        elif isinstance(other, int):
            self.__class__.counts['add'] += 1
            self.value += other
            return self
        else:
            raise TypeError('unsupported operand type(s) for +: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __isub__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['sub'] += 1
            self.value -= other.value
            return self
        elif isinstance(other, int):
            self.__class__.counts['sub'] += 1
            self.value -= other
            return self
        else:
            raise TypeError('unsupported operand type(s) for -: '
                            '{} and {}'.format(self.__class__, type(other)))

    # Logical operations
    def __lt__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['lt'] += 1
            return self.value < other.value
        elif isinstance(other, (int, float)):
            self.__class__.counts['lt'] += 1
            return self.value < other
        else:
            raise TypeError('unsupported operand type(s) for <: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['gt'] += 1
            return self.value > other.value
        elif isinstance(other, (int, float)):
            self.__class__.counts['gt'] += 1
            return self.value > other
        else:
            raise TypeError('unsupported operand type(s) for >: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __le__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['le'] += 1
            return self.value <= other.value
        elif isinstance(other, (int, float)):
            self.__class__.counts['le'] += 1
            return self.value <= other
        else:
            raise TypeError('unsupported operand type(s) for <=: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['ge'] += 1
            return self.value >= other.value
        elif isinstance(other, (int, float)):
            self.__class__.counts['ge'] += 1
            return self.value >= other
        else:
            raise TypeError('unsupported operand type(s) for >=: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['eq'] += 1
            return self.value == other.value
        elif isinstance(other, (int, float)):
            self.__class__.counts['eq'] += 1
            return self.value == other
        else:
            raise TypeError('unsupported operand type(s) for ==: '
                            '{} and {}'.format(self.__class__, type(other)))

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            self.__class__.counts['ne'] += 1
            return self.value != other.value
        elif isinstance(other, (int, float)):
            self.__class__.counts['ne'] += 1
            return self.value != other
        else:
            raise TypeError('unsupported operand type(s) for !=: '
                            '{} and {}'.format(self.__class__, type(other)))
