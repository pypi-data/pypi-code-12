import cf
import datetime
import numpy
import os
import time 
import unittest

class TimeDurationTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]

    def test_TimeDuration(self):        
        self.assertTrue(cf.TimeDuration(2, 'calendar_years') > cf.TimeDuration(1, 'calendar_years'))
        self.assertTrue(cf.TimeDuration(2, 'calendar_years') < cf.TimeDuration(25, 'calendar_months'))
        self.assertTrue(cf.TimeDuration(2, 'hours') <= cf.TimeDuration(1, 'days'))
        self.assertTrue(cf.TimeDuration(2, 'hours') == cf.TimeDuration(1/12.0, 'days'))
        self.assertTrue(cf.TimeDuration(2, 'days') == cf.TimeDuration(48, 'hours'))
        self.assertTrue(cf.TimeDuration(2, 'days') == cf.Data(2))
#        self.assertTrue(cf.TimeDuration(2, 'days') > cf.Data(1.5, ''))
#        self.assertTrue(cf.TimeDuration(2, 'days') > cf.Data(1.5, '1'))
#        self.assertTrue(cf.TimeDuration(2, 'days') < cf.Data(0.03, '100'))
        self.assertTrue(cf.TimeDuration(2, 'days') == cf.Data([2.], 'days'))
        self.assertTrue(cf.TimeDuration(2, 'days') > cf.Data([[60]], 'seconds'))
        self.assertTrue(cf.TimeDuration(2, 'hours') <= 2)
        self.assertTrue(cf.TimeDuration(2, 'days') != 30.5)
        self.assertTrue(cf.TimeDuration(2, 'calendar_years') > numpy.array(1.5))
        self.assertTrue(cf.TimeDuration(2, 'calendar_months') < numpy.array([[12]]))
        
        self.assertFalse(cf.TimeDuration(2, 'calendar_years') <= cf.TimeDuration(1, 'calendar_years'))
        self.assertFalse(cf.TimeDuration(2, 'calendar_years') >= cf.TimeDuration(25, 'calendar_months'))
        self.assertFalse(cf.TimeDuration(2, 'hours') > cf.TimeDuration(1, 'days'))
        self.assertFalse(cf.TimeDuration(2, 'hours') != cf.TimeDuration(1/12.0, 'days'))
        self.assertFalse(cf.TimeDuration(2, 'days') != cf.TimeDuration(48, 'hours'))
        self.assertFalse(cf.TimeDuration(2, 'days') != cf.Data(2))
#        self.assertFalse(cf.TimeDuration(2, 'days') <= cf.Data(1.5, ''))
#        self.assertFalse(cf.TimeDuration(2, 'days') <= cf.Data(1.5, '1'))
#        self.assertFalse(cf.TimeDuration(2, 'days') >= cf.Data(0.03, '100'))
        self.assertFalse(cf.TimeDuration(2, 'days') != cf.Data([2.], 'days'))
        self.assertFalse(cf.TimeDuration(2, 'days') <= cf.Data([[60]], 'seconds'))
        self.assertFalse(cf.TimeDuration(2, 'hours') > 2)
        self.assertFalse(cf.TimeDuration(2, 'days') == 30.5)
        self.assertFalse(cf.TimeDuration(2, 'calendar_years') <= numpy.array(1.5))
        self.assertFalse(cf.TimeDuration(2, 'calendar_months') >= numpy.array([[12]]))
        
        self.assertTrue(cf.TimeDuration(64, 'calendar_years') + 2 == cf.Y(66))
        self.assertTrue(cf.TimeDuration(64, 'calendar_years') - 2.5 == cf.Y(61.5))
        self.assertTrue(cf.M(23) + cf.TimeDuration(64, 'calendar_years') == cf.M(791))
        self.assertTrue(cf.TimeDuration(64, 'calendar_years') + cf.M(24) == cf.Y(66))
        self.assertTrue(cf.TimeDuration(36, 'calendar_months') / numpy.array(8) == cf.M(4))
        self.assertTrue(cf.TimeDuration(36, 'calendar_months') / numpy.array(8.0) == cf.M(36/8.0))
        self.assertTrue(cf.TimeDuration(12, 'calendar_months') * cf.Data([[1.5]]) == cf.Y(1.5))
        self.assertTrue(cf.TimeDuration(36, 'calendar_months') // cf.Data([0.825], '10') == cf.M(4.3))
        self.assertTrue(cf.TimeDuration(36, 'calendar_months') % 10 == cf.M(6))

        self.assertTrue(cf.TimeDuration(24, 'hours') + cf.TimeDuration(0.5, 'days') == cf.h(36.0))
        self.assertTrue(cf.TimeDuration(0.5, 'days') + cf.TimeDuration(24, 'hours') == cf.D(1.5))

        t = cf.TimeDuration(24, 'hours')
        t += 2
        self.assertTrue(t == cf.h(26))
        t -= cf.Data(3, 'hours')
        self.assertTrue(t == cf.h(23))

        t = cf.TimeDuration(24.0, 'hours')
        t += 2
        self.assertTrue(t == cf.h(26))
        t -= cf.Data(2.5, 'hours')
        self.assertTrue(t == cf.h(23.5))
        t *= 2
        self.assertTrue(t == cf.h(47.0))
        t -= 0.5
        self.assertTrue(t == cf.h(46.5))
        t /= 3
        self.assertTrue(t == cf.h(15.5))
        t += 5.5
        self.assertTrue(t == cf.h(21.0))
        t //= numpy.array(2)
        self.assertTrue(t == cf.h(10.0))
        t *= 10
        self.assertTrue(t == cf.h(100.0))
        t %= 3
        self.assertTrue(t == cf.h(1.0))

        self.assertTrue(cf.M().interval(1999, 12) ==
                        (cf.dt('1999-12-01 00:00:00'), cf.dt('2000-01-01 00:00:00')))

        self.assertTrue(cf.Y(2).interval(2000, 2, end=True) == 
                        (cf.dt('1998-02-01 00:00:00'), cf.dt('2000-02-01 00:00:00')))

        self.assertTrue(cf.D(30).interval(1983, 12, 1, 6) ==
                        (cf.dt('1983-12-01 06:00:00'), cf.dt('1983-12-31 06:00:00')))

        self.assertTrue(cf.D(30).interval(1983, 12, 1, 6, end=True) == 
                        (cf.dt('1983-11-01 06:00:00'), cf.dt('1983-12-01 06:00:00')))

        self.assertTrue(cf.D(0).interval(1984, 2, 3) ==
                        (cf.dt('1984-02-03 00:00:00'), cf.dt('1984-02-03 00:00:00')))
        
        self.assertTrue(cf.D(5, hour=6).interval(2004, 3, 2, end=True) ==
                        (cf.dt('2004-02-26 06:00:00'), cf.dt('2004-03-02 06:00:00')))
        
        self.assertTrue(cf.D(5, hour=6).interval(2004, 3, 2, end=True, calendar='noleap') ==
                        (cf.dt('2004-02-25 06:00:00'), cf.dt('2004-03-02 06:00:00')))

        self.assertTrue(cf.D(5, hour=6).interval(2004, 3, 2, end=True, calendar='360_day') ==
                        (cf.dt('2004-02-27 06:00:00'), cf.dt('2004-03-02 06:00:00')))

        self.assertTrue(cf.h(19897.5).interval(1984, 2, 3, 0) ==
                        (cf.dt('1984-02-03 00:00:00'), cf.dt('1986-05-12 01:30:00')))

        self.assertTrue(cf.h(19897.546).interval(1984, 2, 3, 0, end=True) ==
                        (cf.dt('1981-10-26 22:27:14'), cf.dt('1984-02-03 00:00:00')))
    #--- End: def

#--- End: class


#--- End: class

if __name__ == "__main__":
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print''
    unittest.main(verbosity=2)
