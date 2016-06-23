import cf
import datetime
import numpy
import os
import time 

def test():
    start_time = time.time()
    print '----------------------------------------------------------'
    print 'cf.Datetime'
    print '----------------------------------------------------------'

    # ----------------------------------------------------------------
    # cf.Datetime
    # ----------------------------------------------------------------
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

    print "cf.Datatime passed"
    
    # ----------------------------------------------------------------
    # cf.dt
    # ----------------------------------------------------------------
    assert(cf.dt('2001-2-3') ==  cf.Datetime(2001, 2, 3))
    assert(cf.dt('2001-2-3 0:0:0') ==  cf.Datetime(2001, 2, 3))
    assert(cf.dt('2001-2-3 12:30:15') ==  cf.Datetime(2001, 2, 3, 12, 30, 15))
    assert(cf.dt(2001, 2, 3) ==  cf.Datetime(2001, 2, 3))
    assert(cf.dt(2001, 2, 3, 12, 30, 15) ==  cf.Datetime(2001, 2, 3, 12, 30, 15))
    print "cf.dt passed"
    
    # ----------------------------------------------------------------
    # cf.cfdatetime.rt2dt
    # ----------------------------------------------------------------
    assert(cf.cfdatetime.rt2dt(1, cf.Units('days since 2004-2-28')) == 
           numpy.array(datetime.datetime(2004, 2, 29)))
    assert((cf.cfdatetime.rt2dt([1, 3], cf.Units('days since 2004-2-28')) == 
            numpy.array([datetime.datetime(2004, 2, 29), datetime.datetime(2004, 3, 2)])).all())
    assert((cf.cfdatetime.rt2dt([1, 3], cf.Units('days since 2004-2-28', '360_day')) == 
            numpy.array([cf.Datetime(2004, 2, 29), cf.Datetime(2004, 3, 1)])).all())
    print "cf.cfdatetime.rt2dt passed"

    # ----------------------------------------------------------------
    # cf.cfdatetime.dt2rt
    # ----------------------------------------------------------------
    units = cf.Units('days since 2004-2-28')
    assert(cf.cfdatetime.dt2rt(datetime.datetime(2004, 2, 29), None, units) == 
           numpy.array(1.0))
    assert((cf.cfdatetime.dt2rt([datetime.datetime(2004, 2, 29), datetime.datetime(2004, 3, 2)], None, units) == 
            numpy.array([1., 3.])).all())
    units = cf.Units('days since 2004-2-28', '360_day')
    assert((cf.cfdatetime.dt2rt([cf.Datetime(2004, 2, 29), cf.Datetime(2004, 3, 1)], None, units) == 
            numpy.array([1., 3.])).all())
    units = cf.Units('seconds since 2004-2-28')
    assert(cf.cfdatetime.dt2rt(datetime.datetime(2004, 2, 29), None, units) == 
           numpy.array(86400.0)) 
    print "cf.cfdatetime.dt2rt passed"

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Datetime tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
