import threading
import time
import os
import sys
from threading import Timer 

class Monitor(object):

    timer_interval = 1 

    def __init__(self,progress):

        self._progress = progress
        self._seen_so_far = progress.seen_so_far
        self._exit = False

    @property
    def seen_so_far(self):
        return self._seen_so_far

    @seen_so_far.setter
    def seen_so_far(self,value):
        self._seen_so_far = value

    @property
    def is_exit(self):
        return self._exit

    @is_exit.setter
    def is_exit(self,is_exit):
        self._exit = is_exit

    def start_timer(self):
        t = Timer(self.timer_interval,self.monitor)  
        t.start()

    def monitor(self):
        seen_so_far = self.progress.seen_so_far

        percentage = (seen_so_far / float(self.progress.size)) * 100
        time_bytes = seen_so_far - self.seen_so_far
        sec_speed = (time_bytes/1024.0)/self.timer_interval
        sys.stdout.write("\r%s  %s / %s  (%.2f%%),speed:%10.3f KB/S" % (self.progress.filename,\
                        self.progress.seen_so_far,self.progress.size, percentage,sec_speed))

        if percentage == 100:
            sys.stdout.write('\n')
        sys.stdout.flush()

        self.seen_so_far = seen_so_far

        if not self.is_exit:
            self.start_timer()
            
    @property
    def progress(self):
        return self._progress
    

class ProgressPercentage(object):

    def __init__(self, filename,seen_so_far=0): 
        #self._filename = filename
        self._filename = os.path.basename(filename)
        self._size = 0.0 
        self._seen_so_far = seen_so_far 
        self._lock = threading.Lock()
        self._monitor = Monitor(self)
        self.monitor.start_timer()

    @property
    def lock(self):
        return self._lock
    
    @property
    def filename(self):
        return self._filename
    
    @property
    def seen_so_far(self):
        return self._seen_so_far

    @seen_so_far.setter
    def seen_so_far(self,value):
        self._seen_so_far = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self,value):
        self._size = value

    @property
    def monitor(self):
        return self._monitor
    
    def __call__222222222222222(self, bytes_amount):
                # To simplify we'll assume this is hooked up
        # to a single filename.
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / float(self._size)) * 100

            if percentage > 100:
                print self._filename,'upload finished'
                return
            
            
            now_time = time.time()
            if self.first:
                time_sec = now_time - self.start_time
                self.first = False
            else:
                time_sec = now_time - self.last_time
            
            self.time_secs += time_sec
            self.time_bytes += bytes_amount

            if self.time_secs >= self.SPEED_TIME_SEC:
                self.sec_speed = (self.time_bytes/1024.0)/self.time_secs
            #    print 'time sec:',self.time_secs,'bytes_count:',self.time_bytes
                self.time_secs = 0.0
                self.time_bytes = 0.0
         
            sys.stdout.write("\r%s  %s / %s  (%.2f%%),speed:%10.3f KB/S" % (self._filename, self._seen_so_far,\
                                self._size, percentage,self.sec_speed))

            if percentage == 100:
                sys.stdout.write('\n')
            sys.stdout.flush()
            self.last_time = time.time()

    def __call__(self, bytes_amount):
                # To simplify we'll assume this is hooked up
        # to a single filename.
        with self.lock:
            self.seen_so_far += bytes_amount   
            if self.seen_so_far >= self.size:
                self.monitor.is_exit = True
            


class DownloadProgressPercentage(ProgressPercentage):

    def __init__(self, filename,size,seen_so_far=0): 
        super(DownloadProgressPercentage,self).__init__(filename,seen_so_far)
        self.size = size

class UploadProgressPercentage(ProgressPercentage):

    def __init__(self, filename,seen_so_far=0): 
        super(UploadProgressPercentage,self).__init__(filename,seen_so_far)
        self.size = os.path.getsize(filename) 
