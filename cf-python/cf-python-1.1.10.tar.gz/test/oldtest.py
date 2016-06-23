import cf

import os
import time

import test1

import Units
import Data
import Datetime
import Comparison
import Collapse
import PP
import Transform
import create_field
import Aggregate

start_time = time.time()

create_field.test()

Datetime.test()
Comparison.test()
Transform.test()
Aggregate.test()
Units.test()
PP.test()
Collapse.test()
Data.test()

time_elapsed = (time.time() - start_time)/60.0
print
print '---------------------------------------------------------------------------'
print 'All tests passed for cf version', cf.__version__
print 'Running from', os.path.abspath(cf.__file__)
print 'Time elapsed: %f minutes' % time_elapsed
print '---------------------------------------------------------------------------'
