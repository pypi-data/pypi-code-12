
"""
macrolyzer.py

Module that tracks weight trends over time.
"""


import datetime
import myfitnesspal


def main():
    """Retrieves and analyzes weight and body fat from MyFitnessPal."""

    # retrieve and parse command line arguments
    args = parse_args()

    # create MyFitnessPal client
    client = myfitnesspal.Client(args.username, args.password)

    # establish a date range, weeks go from Monday to Sunday
    start_date = datetime.date.today()
    while start_date.weekday() != 6:
        start_date += datetime.timedelta(days=1)
    end_date = (start_date - datetime.timedelta(weeks=args.weeks) +
                datetime.timedelta(days=1))

    # retrieve weight and body fat measurements
    weight = client.get_measurements('Weight', start_date, end_date)
    body_fat = client.get_measurements('Body Fat', start_date, end_date)

    # create list of day objects for every date in the range
    days = create_days(start_date, end_date, weight, body_fat)

    # create week objects from the day objects
    weeks = create_weeks(days)

    # calculate measurement changes week over week
    calculate_changes(weeks)

    # print weekly trend
    for week in weeks:
        print week
        print

    # TODO: Print to HTML


def parse_args():
    """Defines command line argument structure and returns arguments."""

    import argparse

    # create argument parser
    parser = argparse.ArgumentParser(
        description="Macrolyzer - Analyzes weekly weight change over time")

    # define arguments
    credentials = parser.add_argument_group("credentials",
                                            "MyFitnessPal login information")
    credentials.add_argument("username", help="MyFitnessPal username")
    credentials.add_argument("password", help="MyFitnessPal password")
    parser.add_argument("-w",
                        help="number of weeks to analyze \
                              (default: %(default)s)",
                        dest="weeks",
                        type=int,
                        default=5)
    parser.add_argument("-r",
                        help="generate an HTML report",
                        action='store_true',
                        dest="report",
                        default=False)

    # parse the arguments
    args = parser.parse_args()

    return args


def create_days(start_date, end_date, weight, body_fat):
    """Create day objects from measurements."""

    import day

    current_date = start_date
    step = datetime.timedelta(days=1)

    date_range = []

    # create a list of dates within the range
    while current_date >= end_date:
        date_range.append(current_date)
        current_date -= step

    days = []

    # loop over each day in the range
    for date in date_range:
        # retrieve the values for the current day object
        current_date = date
        current_weight = weight.get(current_date, None)
        current_body_fat = body_fat.get(current_date, None)

        # create the day object
        current_day = day.Day(current_date, current_weight, current_body_fat)

        # add the current day to the list of days
        days.append(current_day)

    return days


def create_weeks(days):
    """Create week objects from measurements."""

    import week

    weeks = []

    # loop over each week in the range
    for index in range(0, len(days), 7):

        # create a slice of seven days
        days_list = days[index:index + 7]

        # create the week object
        current_week = week.Week(days_list)

        # add the current week to the list of weeks
        weeks.append(current_week)

    return weeks


def calculate_changes(weeks):
    """Calculates changes in measurements each week."""

    # iterate over all weeks
    for week in weeks:

        # only calulate change if it is not the last week
        if weeks.index(week) == len(weeks) - 1:
            continue

        # retrieve the previous week
        prev_week_index = weeks.index(week) + 1
        prev_week = weeks[prev_week_index]

        # calculate the difference between the measurement values
        week.weight_delta = week.weight_avg - prev_week.weight_avg
        week.lean_body_mass_delta = (week.lean_body_mass_avg -
                                     prev_week.lean_body_mass_avg)
        week.fat_mass_delta = week.fat_mass_avg - prev_week.fat_mass_avg
        week.body_fat_delta = week.body_fat_avg - prev_week.body_fat_avg

if __name__ == "__main__":
    main()
