# -*- coding: utf-8 -*-
# Part of bubble. See LICENSE file for full copyright and licensing details.

try:
    from cProfile import Profile
except ImportError:
    from profile import Profile
from pstats import Stats
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

BUBBLE_PROFILE=False

def start_profile(*argv):
    # https://docs.python.org/3.4/library/profile.html#module-cProfile
    print("start_profile")
    global BUBBLE_PROFILE
    BUBBLE_PROFILE = Profile()
    BUBBLE_PROFILE.enable()

def show_profile(pfile='./logs/profile.out'):
    global BUBBLE_PROFILE
    if not BUBBLE_PROFILE:
        return
    BUBBLE_PROFILE.disable()
    #s = io.StringIO()
    s = StringIO()
    sortby = 'cumulative'
    #ps = Stats(BUBBLE_PROFILE).sort_stats(sortby)
    ps = Stats(BUBBLE_PROFILE,stream=s).sort_stats(sortby)
    ps.print_stats()
    #print(s.getvalue())
    pstats_file='./logs/profiling.pstats'
    profile_text='./logs/profile.txt'
    BUBBLE_PROFILE.dump_stats(pstats_file)
    with open(profile_text,'a+') as pf:
        pf.write(s.getvalue())
    print("end_profile")
    print('pstats_file:'+pstats_file)
    print('profile_text:'+profile_text)

if __name__=='__main__':
    start_profile()
    def ok():pass
    ok()
    show_profile()

