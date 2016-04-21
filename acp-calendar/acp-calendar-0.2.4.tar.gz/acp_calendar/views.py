from datetime import datetime

from jsonview.decorators import json_view

from .models import ACPHoliday


@json_view
def working_days(request, start_date, end_date):
    results = {'start_date': start_date,
               'end_date': end_date,
               'days': '-1',
               }
    try:
        d_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        d_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        days = ACPHoliday.get_working_days(d_start_date, d_end_date)
        results['days'] = str(days)
    except ValueError as e:
        results['error'] = str(e)
    return results

@json_view
def working_delta(request, start_date, days):
    results = {'start_date': start_date,
               'end_date': None,
               'days': days,
               }
    try:
        d_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = ACPHoliday.working_delta(d_start_date, days)
        results['end_date'] = end_date
    except ValueError as e:
        results['error'] = str(e)
    return results
