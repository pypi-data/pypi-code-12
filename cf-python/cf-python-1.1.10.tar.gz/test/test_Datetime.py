import cf
import datetime
import numpy
import os
import time 
import unittest

class DatetimeTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]

    def test_Datetime(self):  
        d = cf.Datetime(2003, 2, 30)
        d = cf.Datetime(2003, 2, 30, 0)
        d = cf.Datetime(2003, 2, 30, 0, 0)
        d = cf.Datetime(2003, 2, 30, 0, 0, 0)
        d = cf.Datetime(2003, 4, 5, 12, 30, 15)
        d = cf.Datetime(year=2003, month=4, day=5, hour=12, minute=30, second=15)
        assert((d.year, d.month, d.day, d.hour, d.minute, d.second) == (2003, 4, 5, 12, 30, 15))
        assert(d.timetuple() == (2003, 4, 5, 12, 30, 15, -1, 1, -1))
        assert((d == d) == True)
        assert((d >  d) == False)
        assert((d >= d) == True)
        assert((d <  d) == False)
        assert((d <= d) == True)
        assert((d != d) == False)
        e = cf.Datetime(2003, 4, 5, 12, 30, 16)
        assert((d == e) == False)
        assert((d >  e) == False)
        assert((d >= e) == False)
        assert((d <  e) == True)
        assert((d <= e) == True)
        assert((d != e) == True)
        e = cf.Datetime(2003, 4, 5, 12, 30, 14)
        assert((d == e) == False)
        assert((d >  e) == True)
        assert((d >= e) == True)
        assert((d <  e) == False)
        assert((d <= e) == False)
        assert((d != e) == True)
    
        d.utcnow()
        cf.Datetime.utcnow()
    #--- End: def    

#    def test_Datetime_dt_cm_cy(self):   
#        self.assertTrue(cf.dt('2001-2-3') ==  cf.Datetime(2001, 2, 3))
#        self.assertTrue(cf.dt('2001-2-3 0:0:0') ==  cf.Datetime(2001, 2, 3))
#        self.assertTrue(cf.dt('2001-2-3 12:30:15') ==  cf.Datetime(2001, 2, 3, 12, 30, 15))
#        self.assertTrue(cf.dt(2001, 2, 3) ==  cf.Datetime(2001, 2, 3))
#        self.assertTrue(cf.dt(2001, 2, 3, 12, 30, 15) ==  cf.Datetime(2001, 2, 3, 12, 30, 15))
#
#        self.assertTrue(cf.cm().months == 1)
#        self.assertTrue(cf.cm(3).months == 3)
#
#        self.assertTrue(cf.cy().years == 1)
#        self.assertTrue(cf.cy(3).years == 3)
#    #--- End: def    

    def test_Datetime_rt2dt(self): 
        self.assertTrue(
            cf.cfdatetime.rt2dt(1, cf.Units('days since 2004-2-28')) == 
            numpy.array(datetime.datetime(2004, 2, 29)))
        self.assertTrue(
            (cf.cfdatetime.rt2dt([1, 3], cf.Units('days since 2004-2-28')) == 
             numpy.array([datetime.datetime(2004, 2, 29), datetime.datetime(2004, 3, 2)])).all())
        self.assertTrue(
            (cf.cfdatetime.rt2dt([1, 3], cf.Units('days since 2004-2-28', '360_day')) == 
             numpy.array([cf.Datetime(2004, 2, 29), cf.Datetime(2004, 3, 1)])).all())
    #--- End: def

    def test_Datetime_dt2rt(self):     
        units = cf.Units('days since 2004-2-28')
        self.assertTrue(
            cf.cfdatetime.dt2rt(datetime.datetime(2004, 2, 29), None, units) ==
            numpy.array(1.0))
        self.assertTrue(
            (cf.cfdatetime.dt2rt([datetime.datetime(2004, 2, 29), datetime.datetime(2004, 3, 2)], None, units) ==
             numpy.array([1., 3.])).all())
        units = cf.Units('days since 2004-2-28', '360_day')
        self.assertTrue((cf.cfdatetime.dt2rt([cf.Datetime(2004, 2, 29), cf.Datetime(2004, 3, 1)], None, units) == numpy.array([1., 3.])).all())
        units = cf.Units('seconds since 2004-2-28')
        self.assertTrue(
            cf.cfdatetime.dt2rt(datetime.datetime(2004, 2, 29), None, units) == 
            numpy.array(86400.0)) 
    #--- End: def

#--- End: class


#--- End: class

if __name__ == "__main__":
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print''
    unittest.main(verbosity=2)
