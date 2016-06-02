# coding=utf-8
from datetime import date
from unittest import TestCase

from ordinaldate import (
    ordinaldate,
    OrdinalDateError,
    Ordinal,
    Weekday,
    Month,
    get_by_values,
    is_week_end
)


class TestOrdinalDate(TestCase):

    def test_ordinal_first(self):
        """Labor Day is a good typical use-case for the Ordinal.first"""
        with open("tests/data_files/labor_day_dates.txt", "r") as dates_file:
            dates_strings_list = dates_file.read().splitlines()

        for date_string in dates_strings_list:
            test_date = date(*[int(p) for p in date_string.split("-")])
            labor_day = get_by_values(Ordinal.first, Weekday.Monday, Month.September, test_date.year)

            self.assertEquals(test_date, labor_day)

    def test_ordinal_second(self):
        """Mother's Day is a good typical use-case for the Ordinal.second"""
        with open("tests/data_files/mothers_day_dates.txt", "r") as dates_file:
            dates_strings_list = dates_file.read().splitlines()

        for date_string in dates_strings_list:
            test_date = date(*[int(p) for p in date_string.split("-")])
            mothers_day = get_by_values(Ordinal.second, Weekday.Sunday, Month.May, test_date.year)

            self.assertEquals(test_date, mothers_day)

    def test_ordinal_third(self):
        """President's Day is a good typical use-case for the Ordinal.third"""
        with open("tests/data_files/presidents_day_dates.txt", "r") as dates_file:
            dates_strings_list = dates_file.read().splitlines()

        for date_string in dates_strings_list:
            test_date = date(*[int(p) for p in date_string.split("-")])
            presidents_day = get_by_values(Ordinal.third, Weekday.Monday, Month.February, test_date.year)

            self.assertEquals(test_date, presidents_day)

    def test_ordinal_fourth(self):
        """Thanksgiving is a good typical use-case for the Ordinal.fourth"""
        with open("tests/data_files/thanksgiving_dates.txt", "r") as dates_file:
            dates_strings_list = dates_file.read().splitlines()

        for date_string in dates_strings_list:
            test_date = date(*[int(p) for p in date_string.split("-")])
            thanksgiving_day = get_by_values(Ordinal.fourth, Weekday.Thursday, Month.November, test_date.year)

            self.assertEquals(test_date, thanksgiving_day)

    def test_ordinal_last(self):
        """Memorial day is unique for being the LAST Monday of the month so it makes a good test."""
        with open("tests/data_files/memorial_day_dates.txt", "r") as dates_file:
            dates_strings_list = dates_file.read().splitlines()

        for date_string in dates_strings_list:
            test_date = date(*[int(p) for p in date_string.split("-")])
            memorial_day = get_by_values(Ordinal.last, Weekday.Monday, Month.May, test_date.year)

            self.assertEquals(test_date, memorial_day)

    def test_integer_params(self):
        """Allow end users to pass integers as params rather than the Enum values"""
        test_date = get_by_values(4, 5, 6, 2016)
        self.assertEquals(test_date, date(2016, 6, 25))

    def test_integer_params_month_not_in_range(self):

        # First verify that the exception is raised.
        with self.assertRaises(expected_exception=OrdinalDateError):
            get_by_values(8, 3, 13, 2015)

        # Then verify that the message is the correct one.
        try:
            get_by_values(8, 3, 13, 2015)
        except OrdinalDateError as e:
            message = "`13` is not in range 1..12"
            self.assertEquals(message, str(e))

    def test_integer_params_ordinal_not_in_range(self):

        # First verify that the exception is raised.
        with self.assertRaises(expected_exception=OrdinalDateError):
            get_by_values(8, 3, 12, 2015)

        # Then verify that the message is the correct one.
        try:
            get_by_values(8, 3, 12, 2015)
        except OrdinalDateError as e:
            message = "Month `December` does not have 8 Thursdays in it!"
            self.assertEquals(message, str(e))

    def test_integer_params_weekday_not_in_range(self):

        # First verify that the exception is raised.
        with self.assertRaises(expected_exception=OrdinalDateError):
            get_by_values(2, 8, 12, 2015)

        # Then verify that the message is the correct one.
        try:
            get_by_values(2, 8, 12, 2015)
        except OrdinalDateError as e:
            message = "`8` is not in range 0..6"
            self.assertEquals(message, str(e))

    def test_param_year_is_none(self):
        """Ensure that if param `year` is None that the current year is used"""
        test_date = get_by_values(Ordinal.first, Weekday.Saturday, Month.May)
        self.assertEquals(date.today().year, test_date.year)

    def test_is_weekend_true(self):
        self.assertTrue(is_week_end(date(2016, 5, 28)))
        self.assertTrue(is_week_end(date(2016, 5, 29)))

    def test_is_weekend_false(self):
        self.assertFalse(is_week_end(date(2016, 5, 27)))
        self.assertFalse(is_week_end(date(2016, 5, 30)))

    def test_ordinal_date(self):

        ordinals = ["first", "second", "third", "fourth", "fifth", "last"]
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        months = [
            "january", "february", "march",
            "april", "may", "june",
            "july", "august", "september",
            "october", "november", "december"
        ]

        # Build up every possible way to call the syntactic sugar way of creating dates
        # EX: `ordinaldate.first.monday.january` through `ordinaldate.last.sunday.december`
        for ordinal in ordinals:
            for weekday in weekdays:
                for month in months:
                    try:
                        test_date = eval("ordinaldate.{}.{}.{}".format(ordinal, weekday, month))
                        base_date = get_by_values(
                            getattr(Ordinal, ordinal),
                            getattr(Weekday, weekday.title()),
                            getattr(Month, month.title())
                        )
                        self.assertEquals(base_date, test_date)

                    except OrdinalDateError:
                        # None of the months have five of every single weekday.
                        pass
