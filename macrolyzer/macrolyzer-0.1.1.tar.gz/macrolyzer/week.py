"""
week.py

Implements the week class.
"""


class Week(object):
    """Class which models a Week of measurements."""

    def __init__(self, days):
        self.days = days

        # averages
        self.weight_avg = None
        self.lean_body_mass_avg = None
        self.fat_mass_avg = None
        self.body_fat_avg = None

        # deltas
        self.weight_delta = None
        self.lean_body_mass_delta = None
        self.fat_mass_delta = None
        self.body_fat_delta = None

        # calculate weight average
        avg_list = [day.weight for day in days if day.weight]
        self.weight_avg = average(avg_list)

        # calculate lean body mass average
        avg_list = [day.lean_body_mass for day in days if day.lean_body_mass]
        self.lean_body_mass_avg = average(avg_list)

        # calculate fat mass average
        avg_list = [day.fat_mass for day in days if day.fat_mass]
        self.fat_mass_avg = average(avg_list)

        # calculate body fat average
        avg_list = [day.body_fat for day in days if day.body_fat]
        self.body_fat_avg = average(avg_list)

    def __str__(self):
        week_string = ""

        for day in self.days:
            week_string += str(day) + '\n'

        week_string += '\n'

        week_string += "%5s   " % ("avg")

        week_string += "w: %5.5s   lbm: %5.5s   fm: %5.5s   bf: %5.5s" % (
            self.weight_avg,
            self.lean_body_mass_avg,
            self.fat_mass_avg,
            self.body_fat_avg)

        week_string += '\n'

        week_string += "%5s   " % ("delta")

        week_string += "w: %5.5s   lbm: %5.5s   fm: %5.5s   bf: %5.5s" % (
            self.weight_delta,
            self.lean_body_mass_delta,
            self.fat_mass_delta,
            self.body_fat_delta)

        return week_string


def average(avg_list):
    """Averages all values in the list."""

    if len(avg_list) == 0:
        return 0
    
    avg = sum(avg_list) / len(avg_list)

    return avg
