#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import itertools
import threading
import sys
import time
from afapatterns import Patterns

class Animation():
    
    def __init__(self, text=u'Loading', end_text=u'Done!', pattern=Patterns.DEFAULT, interval=0.1):
        self.end = False
        self.pattern = pattern
        self.text = text
        self.end_text = end_text
        self.interval = interval
    
    def start(self):
        t = threading.Thread(target=self.animation)
        t.start()
        
    def stop(self):
        self.end = True
        
    def animation(self):
        for c in itertools.cycle(self.pattern):
            if self.end:
                break
            sys.stdout.write('\r%s %s ' % (self.text, c))
            sys.stdout.flush()
            time.sleep(self.interval)
        sys.stdout.write('\r%s\n' % self.get_end_txt(c))
        sys.stdout.flush()
    
    def get_end_txt(self, cycle):
        total_length = len(self.text + self.end_text + cycle)
        ret = self.end_text.ljust(total_length)
        return ret