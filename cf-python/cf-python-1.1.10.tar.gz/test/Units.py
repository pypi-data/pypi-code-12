import cf
import math
import os
import time 

def test():
    start_time = time.time()
    print '----------------------------------------------------------'
    print 'cf.Units'
    print '----------------------------------------------------------'

    # ----------------------------------------------------------------
    # cf.Units.equals
    # ----------------------------------------------------------------
    assert cf.Units('m')==cf.Units('m')
    assert cf.Units('m')==cf.Units('metres')
    assert cf.Units('m')==cf.Units('meTRES')
        
    assert cf.Units('days since 2000-1-1')==cf.Units('d since 2000-1-1 0:0')
    assert cf.Units('days since 2000-1-1')!=cf.Units('h since 1234-1-1 0:0')

    assert cf.Units('days since 2000-1-1')==cf.Units('d since 2000-1-1 0:0', calendar='gregorian')
    assert cf.Units('days since 2000-1-1')==cf.Units('d since 2000-1-1 0:0', calendar='standard')

    assert cf.Units(calendar='noleap')==cf.Units(calendar='noleap')
    assert cf.Units(calendar='noleap')==cf.Units(calendar='365_day')
    assert cf.Units(calendar='nOLEAP')==cf.Units(calendar='365_dAY')

    assert cf.Units('days since 2000-1-1', calendar='all_leap')==cf.Units('d since 2000-1-1 0:0', calendar='366_day')
    assert cf.Units('days since 2000-1-1', calendar='all_leap')!=cf.Units('h since 2000-1-1 0:0', calendar='366_day')

    print "cf.Units.equals passed"
 
    # ----------------------------------------------------------------
    # cf.Units.equivalent
    # ----------------------------------------------------------------
    assert cf.Units('m').equivalent(cf.Units('m'))
    assert cf.Units('meter').equivalent(cf.Units('km'))
    assert cf.Units('metre').equivalent(cf.Units('mile'))
        
    assert cf.Units('s').equivalent(cf.Units('h'))
    assert cf.Units('s').equivalent(cf.Units('day'))
    assert cf.Units('second').equivalent(cf.Units('month'))    

    assert cf.Units(calendar='noleap').equivalent(cf.Units(calendar='noleap'))
    assert cf.Units(calendar='noleap').equivalent(cf.Units(calendar='365_day'))
    assert cf.Units(calendar='nOLEAP').equivalent(cf.Units(calendar='365_dAY'))

    assert cf.Units('days since 2000-1-1').equivalent(cf.Units('d since 2000-1-1 0:0'))
    assert cf.Units('days since 2000-1-1').equivalent(cf.Units('h since 1234-1-1 0:0'))

    assert cf.Units('days since 2000-1-1').equivalent(cf.Units('d since 2000-1-1 0:0', calendar='gregorian'))
    assert cf.Units('days since 2000-1-1').equivalent(cf.Units('h since 1234-1-1 0:0', calendar='standard'))

    assert cf.Units('days since 2000-1-1', calendar='all_leap').equivalent(cf.Units('d since 2000-1-1 0:0', calendar='366_day'))
    assert cf.Units('days since 2000-1-1', calendar='all_leap').equivalent(cf.Units('h since 1234-1-1 0:0', calendar='366_day'))

    print "cf.Units.equivalent passed"
 
    # ----------------------------------------------------------------
    # cf.Units arithmetic
    # ----------------------------------------------------------------
    assert (cf.Units('m')*2)    ==cf.Units('2m')
    assert (cf.Units('m')/2)    ==cf.Units('0.5m')
    assert (cf.Units('m')//2)   ==cf.Units('0.5m')
    assert (cf.Units('m')+2)    ==cf.Units('m @ -2')
    assert (cf.Units('m')-2)    ==cf.Units('m @ 2')
    assert (cf.Units('m')**2)   ==cf.Units('m2')
    assert (cf.Units('m')**-2)  ==cf.Units('m-2')
    assert (cf.Units('m2')**0.5)==cf.Units('m')

    u = cf.Units('m')
    v = u
    u *= 2
    assert u==cf.Units('2m')
    assert u!=v
    u = cf.Units('m')
    v = u
    u /= 2
    assert u==cf.Units('0.5m')
    assert u!=v
    u = cf.Units('m')
    v = u
    u //= 2
    assert u==cf.Units('0.5m')
    assert u!=v
    u = cf.Units('m')
    v = u
    u += 2
    assert u==cf.Units('m @ -2')
    assert u!=v
    u = cf.Units('m')
    v = u
    u -= 2
    assert u==cf.Units('m @ 2')
    assert u!=v
    u = cf.Units('m')
    v = u
    u **= 2
    assert u==cf.Units('m2')
    assert u!=v

    assert (2*cf.Units('m')) ==cf.Units('2m')
    assert (2/cf.Units('m')) ==cf.Units('2 m-1')
    assert (2//cf.Units('m'))==cf.Units('2 m-1')
    assert (2+cf.Units('m')) ==cf.Units('m @ -2')
    assert (2-cf.Units('m')) ==cf.Units('-1 m @ -2')

    assert (cf.Units('m')*cf.Units('2m')) ==cf.Units('2 m2')
    assert (cf.Units('m')/cf.Units('2m')) ==cf.Units('0.5')
    assert (cf.Units('m')//cf.Units('2m'))==cf.Units('0.5')

    u = cf.Units('m')
    v = u
    u *= u
    assert u==cf.Units('m2')
    assert u!=v
    u = cf.Units('m')
    v = u
    u /= u
    assert u==cf.Units('1')
    assert u!=v
    u = cf.Units('m')
    v = u
    u //= u
    assert u==cf.Units('1')
    assert u!=v

    assert cf.Units('m').log(10)    ==cf.Units('lg(re 1 m)')
    assert cf.Units('m').log(2)     ==cf.Units('lb(re 1 m)')
    assert cf.Units('m').log(math.e)==cf.Units('ln(re 1 m)')
    assert cf.Units('m').log(1.5)   ==cf.Units('2.46630346237643 ln(re 1 m)')

    print "cf.Units arithmetic passed"

    time_elapsed = (time.time() - start_time)/60.0
    print
    print '---------------------------------------------------------------------------'
    print 'All cf.Units tests passed for cf version', cf.__version__
    print 'Running from', os.path.abspath(cf.__file__)
    print 'Time elapsed: %f minutes' % time_elapsed
    print '---------------------------------------------------------------------------' 
    print
#--- End: def

if __name__ == "__main__":
    test()
