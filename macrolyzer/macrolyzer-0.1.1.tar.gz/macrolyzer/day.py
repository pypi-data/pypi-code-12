"""
day.py

Implements the day class.
"""


class Day(object):
    """Class which models a Day of measurements."""

    def __init__(self, date, weight, body_fat):
        self.date = date
        self.weight = weight
        self.body_fat = body_fat
        self.fat_mass = None
        self.lean_body_mass = None

        # calulate only if weight and body fat have values
        if weight and body_fat:
            # calculate fat mass
            self.fat_mass = self.weight * (self.body_fat / 100)

            # calculate lean body mass
            self.lean_body_mass = self.weight - self.fat_mass

    def __str__(self):
        day_string = "%5s   " % ("day")

        day_string += "w: %5.5s   lbm: %5.5s   fm: %5.5s   bf: %5.5s   " % (
            self.weight,
            self.lean_body_mass,
            self.fat_mass,
            self.body_fat)

        day_string += "d: %s" % (str(self.date))

        return day_string
