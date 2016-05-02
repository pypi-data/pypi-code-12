from calendar import IllegalMonthError
from datetime import datetime

from jsonview.decorators import json_view

from .models import ACPHoliday, ACPCalendarException


@json_view
def working_days(request, start_date, end_date):
    results = {'start_date': start_date,
               'end_date': end_date,
               'days': '-1',
               }
    try:
        days = ACPHoliday.get_working_days(start_date, end_date)
        results['days'] = str(days)
    except ACPCalendarException as e:
        results['error'] = str(e)

    return results

@json_view
def working_delta(request, start_date, days):
    results = {'start_date': start_date,
               'end_date': None,
               'days': days,
               }
    try:
        end_date = ACPHoliday.working_delta(start_date, days)
        results['end_date'] = end_date
    except ACPCalendarException as e:
        results['error'] = str(e)

    return results

@json_view()
def working_days_in_month(request, year, month):
    results = {'year': year,
               'month': month,
               'days': '-1',
               }
    try:
        results['days'] = str(ACPHoliday.get_working_days_for_month(int(year), int(month)))
    except ACPCalendarException as e:
        results['error'] = str(e)
    return results
