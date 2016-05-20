#!/usr/bin/env python

from datetime import datetime, timedelta
import sys

import dateparser
import dateutil.tz

# 0: Monday
# 6: Sunday
START_OF_WEEK = 6

class DateRange(object):
	def __init__(self, start=None, end=None):
		now = datetime.now(dateutil.tz.tzlocal())
		self.week = start == "week"
		if self.week:
			start = self.first_of_week(now, end)
			end = start + timedelta(days=6)
		else:
			if start is None:
				start = now
				end = start
			else:
				start = self.parse_date(start)
				end = start if end is None else self.parse_date(end)
		start = start.replace(hour=0, minute=0, second=0, microsecond=0)
		end = end.replace(hour=0, minute=0, second=0, microsecond=0)
		self.one_day = start == end
		if self.one_day:
			self.dates = "{:%Y-%m-%d}".format(start)
		else:
			self.dates = "{:%Y-%m-%d} - {:%Y-%m-%d}".format(start, end)
		self.start = start
		self.end = end + timedelta(days=1)

	def decrement_week(self):
		if self.week:
			self.start -= timedelta(weeks=1)
			self.end -= timedelta(weeks=1)
			self.dates = "{:%Y-%m-%d} - {:%Y-%m-%d}".format(self.start,
			                                                self.end - timedelta(days=1))

	def decrement_day(self):
		if self.one_day:
			self.start -= timedelta(days=1)
			self.end -= timedelta(days=1)
			self.dates = "{:%Y-%m-%d}".format(self.start)

	@staticmethod
	def first_of_week(date, offset):
		if offset is None:
			offset = 0
		else:
			try:
				offset = int(offset)
			except ValueError:
				raise WeeksParseError(offset)
		days = (date.weekday() - START_OF_WEEK) % 7 - (7 * offset)
		date -= timedelta(days=days)
		return date

	@staticmethod
	def parse_date(date):
		now = datetime.now(dateutil.tz.tzlocal())
		settings = {'TIMEZONE': now.tzname(), 'RETURN_AS_TIMEZONE_AWARE': True}
		result = dateparser.parse(date, settings=settings)
		if result is None:
			raise DateParseError(date)
		result -= result.utcoffset()
		# last = now
		corrected = result.replace(tzinfo=dateutil.tz.tzlocal())
		while result.utcoffset() != corrected.utcoffset():
			settings['TIMEZONE'] = corrected.tzname()
			# last = result
			result = dateparser.parse(date, settings=settings)
			if result is None:
				raise DateParseError(date)
			result -= result.utcoffset()
			corrected = result.replace(tzinfo=dateutil.tz.tzlocal())
		return result.replace(tzinfo=dateutil.tz.tzlocal())

	def tuple(self):
		return self.start, self.end

class DateParseError(ValueError):
	def __init__(self, date):
		super(DateParseError, self).__init__("date format not supported: '{}'".format(date))

class WeeksParseError(ValueError):
	def __init__(self, weeks):
		super(WeeksParseError, self).__init__("invalid number of weeks: '{}'".format(weeks))

def process_entries(entries):
	days = {}
	for entry in entries:
		desc, dur = entry['description'], entry['duration']
		date = entry['start'][:len('YYYY-MM-DD')]
		if date not in days:
			days[date] = {}
		if desc not in days[date]:
			days[date][desc] = 0
		days[date][desc] += dur

	rows = []
	for date, work in sorted(days.items()):
		rows.append([])
		rows.append([date])
		work_rt = 0
		work_ct = timedelta()
		for name, dur in sorted(work.items()):
			record = hmi(dur)
			clock = timedelta(seconds=dur)
			rows.append([name, str(clock), hm(record)])
			work_rt += record
			work_ct += clock
		rows.append(["TOTAL", hms_td(work_ct), hm(work_rt)])

	return rows

def hms_td(td):
    hours, rem = divmod(td.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    hours += td.days * 24
    #result = '{:02d}'.format(seconds)
    result = []
    if hours > 0:
    	result.append('{:d}'.format(hours))
    if result or minutes > 0:
    	result.append('{:02d}'.format(minutes))
	result.append('{:02d}'.format(seconds))
    return ':'.join(result)

def hmi(s, round=15*60):
	return ((s + round/2) // round) * round

def hm(s):
	td = timedelta(seconds=s)
	h = td.days * 24 + td.seconds // 3600
	m = (td.seconds//60)%60
	result = '{}m'.format(m)
	if h > 0:
		result = '{}h {}'.format(h, result)
	return result
