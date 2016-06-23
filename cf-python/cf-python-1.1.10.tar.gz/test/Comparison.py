import cf
import datetime
import numpy
import os
import time

def test():
    start_time = time.time()

    print '----------------------------------------------------------'
    print 'cf.Comparison'
    print '----------------------------------------------------------'
    chunksize = cf.CHUNKSIZE()
    cf.CHUNKSIZE(17)

    # ----------------------------------------------------------------
    # cf.eq
    # cf.ne
    # cf.ge
    # cf.gt
    # cf.le
    # cf.lt
    # cf.wi
    # cf.wo
    # cf.set
    # ----------------------------------------------------------------
    d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:57:57')   
    assert((d==cf.eq(cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[False, True], [False, False]])))
    assert((d==cf.ne(cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[True, False], [True, True]])))
    assert((d==cf.ge(cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[False, True], [True, False]])))
    assert((d==cf.gt(cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[False, False], [True, False]])))
    assert((d==cf.le(cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[True, True], [False, True]])))
    assert((d==cf.lt(cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[True, False], [False, True]]))) 
    assert((d==cf.wi(cf.dt('2000-12-31 21:57:57 21:57:57'), cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[False, True], [False, True]]))) 
    assert((d==cf.wo(cf.dt('2000-12-31 21:57:57 21:57:57'), cf.dt('2001-01-03 21:57:57'))).equals(cf.Data([[True, False], [True, False]]))) 
    assert((d==cf.set([cf.dt('2000-12-31 21:57:57 21:57:57'), cf.dt('2001-01-03 21:57:57')])).equals(cf.Data([[False, True], [False, True]]))) 

    print 'cf.eq passed'
    print 'cf.ne passed'
    print 'cf.ge passed'
    print 'cf.gt passed'
    print 'cf.le passed'
    print 'cf.lt passed'
    print 'cf.wi passed'
    print 'cf.wo passed'
    print 'cf.set passed'

    # ----------------------------------------------------------------
    # cf.year
    # cf.month
    # cf.day
    # cf.hour 
    # cf.minute
    # cf.second
    # ----------------------------------------------------------------
    d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:57:57')   
    assert((d==cf.year(2000)).equals(cf.Data([[True, False], [False, True]])))
    assert((d==cf.month(12)).equals(cf.Data([[True, False], [False, True]])))
    assert((d==cf.day(3)).equals(cf.Data([[False, True], [False, False]])))
    d = cf.Data([[1., 5], [6, 2]], 'hours since 2000-12-29 21:57:57')
    assert((d==cf.hour(2)).equals(cf.Data([[False, True], [False, False]])))
    d = cf.Data([[1., 5], [6, 2]], 'minutes since 2000-12-29 21:57:57')
    assert((d==cf.minute(2)).equals(cf.Data([[False, True], [False, False]])))
    d = cf.Data([[1., 5], [6, 2]], 'seconds since 2000-12-29 21:57:57')
    assert((d==cf.second(2)).equals(cf.Data([[False, True], [False, False]]))) 

    d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:57:57')   
    assert((d==cf.year(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
    assert((d==cf.month(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
    assert((d==cf.day(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
    d = cf.Data([[1., 5], [6, 2]], 'hours since 2000-12-29 21:57:57')
    assert((d==cf.hour(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
    d = cf.Data([[1., 5], [6, 2]], 'minutes since 2000-12-29 21:57:57')
    assert((d==cf.minute(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
    d = cf.Data([[1., 5], [6, 2]], 'seconds since 2000-12-29 21:57:57')
    assert((d==cf.second(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]]))) 

    print 'cf.year passed'
    print 'cf.month passed'
    print 'cf.day passed'
    print 'cf.hour passed'
    print 'cf.minute passed'
    print 'cf.second passed'

    # ----------------------------------------------------------------
    # cf.dteq
    # cf.dtne
    # cf.dtge
    # cf.dtgt
    # cf.dtle
    # cf.dtlt
    # ----------------------------------------------------------------
    d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:57:57')   
    assert((d==cf.dteq('2001-01-03 21:57:57')).equals(cf.Data([[False, True], [False, False]])))
    assert((d==cf.dtne('2001-01-03 21:57:57')).equals(cf.Data([[True, False], [True, True]])))
    assert((d==cf.dtge('2001-01-03 21:57:57')).equals(cf.Data([[False, True], [True, False]])))
    assert((d==cf.dtgt('2001-01-03 21:57:57')).equals(cf.Data([[False, False], [True, False]])))
    assert((d==cf.dtle('2001-01-03 21:57:57')).equals(cf.Data([[True, True], [False, True]])))
    assert((d==cf.dtlt('2001-01-03 21:57:57')).equals(cf.Data([[True, False], [False, True]]))) 

    assert((d==cf.dteq(2001, 1, 3, 21, 57, 57)).equals(cf.Data([[False, True], [False, False]])))
    assert((d==cf.dtne(2001, 1, 3, 21, 57, 57)).equals(cf.Data([[True, False], [True, True]])))
    assert((d==cf.dtge(2001, 1, 3, 21, 57, 57)).equals(cf.Data([[False, True], [True, False]])))
    assert((d==cf.dtgt(2001, 1, 3, 21, 57, 57)).equals(cf.Data([[False, False], [True, False]])))
    assert((d==cf.dtle(2001, 1, 3, 21, 57, 57)).equals(cf.Data([[True, True], [False, True]])))
    assert((d==cf.dtlt(2001, 1, 3, 21, 57, 57)).equals(cf.Data([[True, False], [False, True]]))) 

    d = cf.dt(2002, 6, 16)
    assert(not (d == cf.dteq(1990, 1, 1)))
    assert(d == cf.dteq(2002, 6, 16))
    assert(not(d == cf.dteq('2100-1-1')))
    assert(not (d == cf.dteq('2001-1-1') & cf.dteq(2010, 12, 31)))

    d = cf.dt(2002, 6, 16)
    assert(d == cf.dtge(1990, 1, 1))
    assert(d == cf.dtge(2002, 6, 16))
    assert(not (d == cf.dtge('2100-1-1')))
    assert(not (d == cf.dtge('2001-1-1') & cf.dtge(2010, 12, 31)))
                                
    d = cf.dt(2002, 6, 16)
    assert(d == cf.dtgt(1990, 1, 1))
    assert(not (d == cf.dtgt(2002, 6, 16)))
    assert(not (d == cf.dtgt('2100-1-1')))
    assert(d == cf.dtgt('2001-1-1') & cf.dtle(2010, 12, 31))

    d = cf.dt(2002, 6, 16)
    assert(d == cf.dtne(1990, 1, 1))
    assert(not (d == cf.dtne(2002, 6, 16)))
    assert(d == cf.dtne('2100-1-1'))
    assert(d == cf.dtne('2001-1-1') & cf.dtne(2010, 12, 31))

    d = cf.dt(2002, 6, 16)
    assert(not (d == cf.dtle(1990, 1, 1)))
    assert(d == cf.dtle(2002, 6, 16))
    assert(d == cf.dtle('2100-1-1'))
    assert(not (d == cf.dtle('2001-1-1') & cf.dtle(2010, 12, 31)))

    d = cf.dt(2002, 6, 16)
    assert(not (d == cf.dtlt(1990, 1, 1)))
    assert(not (d == cf.dtlt(2002, 6, 16)))
    assert(d == cf.dtlt('2100-1-1'))
    assert(not (d == cf.dtlt('2001-1-1') & cf.dtlt(2010, 12, 31)))

    print 'cf.dteq passed'
    print 'cf.dtne passed'
    print 'cf.dtge passed'
    print 'cf.dtgt passed'
    print 'cf.dtle passed'
    print 'cf.dtlt passed'

    cf.CHUNKSIZE(chunksize)

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Comparison tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
