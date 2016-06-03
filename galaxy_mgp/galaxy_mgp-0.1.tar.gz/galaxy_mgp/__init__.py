from datetime import datetime, timedelta

def say_distance(ffrom=None, tto=None):
    if (ffrom is None | tto is None):
        ffrom = "Sun"
        tto = "Self"
        print "the distance from %s and %s is %f" % (ffrom, tto, 0)
    else:
        print "the distance from %s and %s is %f" % (ffrom, tto ,987889.090)
