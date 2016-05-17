#!/usr/bin/env python

import pytz

# TODO astimezone !
# TODO safe with _...
# USE UTC where possible
# if you carry tzoffset helps to be more excate (duplicates in local timezone)
# not all operations are possible (e.g add hours if tz != utc)
# default os.environ['TZ']

from momentx_wrapper import MomentXWrapper

if __name__ == '__main__':
    def test():
        moment = MomentXWrapper("Europe/Berlin")
#         print moment.now()
#         print moment.utcnow()
#         print moment.utc([2012, 12, 19])
#         a = moment.date("2016-01-30 01:02:03+0100")
        a = moment.date("2016-01-06 19:52:12")
        b = a.zero()
        print a
        print b
#         print moment.date("2016-01-30 01:00:00+0100").add(months=-1)
#         print moment.date("2016-03-27 01:30:00+0100").add(hours=6)
#         print moment.date("2016-03-27 01:30:00+0100").add(hours=1) #raises Error
#         print moment.date("2016-03-26 02:30:00+0100").add(days=1) #raises Error
        return

#         print moment.date("2016-01-12 01:00:00")
#         print moment.date("2016-07-12 01:00:00")

#         print moment.date("2016-01-12 01:00:00+0100", timezone="Europe/Berlin")
#         print moment.date("2016-07-12 01:00:00+0200", timezone="Europe/Berlin")
#         return


        a = moment.date("2016-01-12 01:00:00+0100")
        b = moment.utc("2016-01-12 00:00:00+0000")

        print "---"
        print a
        print b
        print a == b
        # but !!!
        c = a.clone().add(months=6)
        d = b.clone().add(months=6)
        print a
        print b
        print c
        print d

        print c == d
        print (a.add(months=6)) == (b.add(months=6))
        print c
        print d

        print "---"
        return


        print moment.date("2016-01-06 19:52:12+0100", timezone="Europe/London")
        print moment.now()
        print moment.now().hours # e.g.12
        print moment.utcnow().hours # e.g. 11
        print moment.now().zero._date < moment.utcnow().zero._date # TODO
        print moment.now().replace(seconds=0, microseconds=0)._date.astimezone(pytz.utc)
        print moment.utcnow().replace(seconds=0, microseconds=0)._date.astimezone(pytz.utc)
        print moment.now().replace(seconds=0, microseconds=0)._date.astimezone(pytz.utc) == moment.utcnow().replace(seconds=0, microseconds=0)._date.astimezone(pytz.utc)

        print moment.now().replace(seconds=0, microseconds=0)._date
        print moment.utcnow().replace(seconds=0, microseconds=0)._date
        print moment.now().replace(seconds=0, microseconds=0)._date == moment.utcnow().replace(seconds=0, microseconds=0)._date


        print moment.date("December 18, 2012", "MMMM D, YYYY")
        print moment.date("2035-01-01 00:00:00+0000", "%Y-%m-%d %H:%M:%S%z")
        print moment.date("2035-01-01 00:00:00+0000", "%Y-%m-%d %H:%M:%S%z")
        print repr(moment.date("2035-01-01 00:00:00+0000", "%Y-%m-%d %H:%M:%S%z"))
        print moment.date("2016-01-10 15:18:00.444347+0000")
        print moment.date("2035-01-01 00:00:00+0000")
        print moment.date("2035-01-01 00:00:00")
        print moment.date("2035-01-01")

    def test2():
        """ test to fake 'now' """
        import time
        import datetime
        now = datetime.datetime(2012, 12, 18, tzinfo=pytz.utc)
        moment = MomentXWrapper("Europe/Berlin", now=now)
#         moment = MomentXWrapper(default_timezone="Europe/Berlin")
        print moment.now()
        print moment.utcnow()
        time.sleep(1)
        print moment.utcnow()


# print moment.now() # datetime?
# print moment.now().tzinfo # datetime?
# print moment.date("December 18, 2012", "MMMM D, YYYY")
# print moment.now().year # datetime?
# print moment.unix(1355788800000, utc=True)
# print moment.date(2012, 12, 18, 1, 2, 3).zero
# print moment.utc((2012, 12, 18)).replace(hours=1).add(minutes=2).replace(seconds=3)

# print moment.utcnow().zero.replace(hours=1).add(minutes=2).replace(seconds=3)
# print moment.utcnow().zero.replace(hours=1).add(minutes=2).replace(seconds=3).add(days=2)
# print moment.utcnow().zero.replace(hours=1).add(minutes=2).replace(seconds=3).add(days=2).year

#     test()
    test2()
