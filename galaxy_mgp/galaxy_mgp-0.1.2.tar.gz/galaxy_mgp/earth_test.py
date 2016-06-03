from datetime import datetime, timedelta

def say_distance(ffrom=None, tto=None):
    print "ffrom =%s and tto = %s" %(ffrom, tto)
    if ((ffrom is None) or (tto is None)):
        ffrom = "Sun"
        tto = "Self"
        print "the distance from %s and %s is %f" % (ffrom, tto, 0)
    else:
        print "the distance from %s and %s is %f" % (ffrom, tto ,987889.090)


def checkDistance():
    ffrom = "Sun"
    tto = "Earth"
    say_distance(ffrom, tto)

if __name__ == "__main__":
    checkDistance()
