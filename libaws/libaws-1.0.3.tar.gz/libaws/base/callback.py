#coding:utf-8
import threading
import time
import os
import sys

class Monitor(object):
    '''
        监控下载上传速度和进度的计时器类
    '''
    #监控下载/上传速度的时间间隔 
    timer_interval = 1 

    def __init__(self,progress):
        self.daemon = True
        self._progress = progress
        self._seen_so_far = progress.seen_so_far
        self._exit = False
        self._progress_type = ''

        if progress.type == progress.DOWNLOAD_PROGRESS:
            self._progress_type= '↓'
	elif progress.type == progress.UPLOAD_PROGRESS:
            self._progress_type= '↑'

    @property
    def seen_so_far(self):
        '''
            上一次下载/上传的字节数
        '''
        return self._seen_so_far

    @seen_so_far.setter
    def seen_so_far(self,value):
        self._seen_so_far = value

    @property
    def is_exit(self):
        '''
            停止监控
        '''
        return self._exit

    @is_exit.setter
    def is_exit(self,is_exit):
        self._exit = is_exit

    def start_timer(self):
        t = threading.Timer(self.timer_interval,self.monitor)  
        t.start()

    def monitor(self):
        '''
            实时打印下载/上传速度
        '''
        if 0 == self.progress.size:
            return

        seen_so_far = self.progress.seen_so_far
        percentage = (seen_so_far / float(self.progress.size)) * 100
        time_bytes = seen_so_far - self.seen_so_far
        sec_speed = (time_bytes/1024.0)/self.timer_interval
        sys.stdout.write("\r%s %s  %s / %s  (%.2f%%),speed:%10.3f KB/S" % (self.progress.filename,\
                                self._progress_type,self.progress.seen_so_far,self.progress.size, percentage,sec_speed))

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
    ''' 
        进度条
    '''

    #上传进度条
    UPLOAD_PROGRESS = 1
    #下载进度条
    DOWNLOAD_PROGRESS = 2

    def __init__(self, filename,progress_type,seen_so_far=0): 
        self._filename = filename
        self._size = 0.0 
        self._seen_so_far = seen_so_far 
        #进度条类型
        self._type = progress_type
        self._lock = threading.Lock()
        self._monitor = Monitor(self)
        #监控计时器是否启动,刚开始时未启动
        self._is_timer_start = False

    @property
    def lock(self):
        '''
            互斥锁
        '''
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
        if value < 0:
            raise ValueError('progress size must not less 0')

        self._size = value

    @property
    def monitor(self):
        return self._monitor

    @property
    def type(self):
        return self._type

    def __call__(self, bytes_amount):
    
        with self.lock:
            #只启动一次计时器就可以了
            if not self._is_timer_start: 
                self.monitor.start_timer()
                self._is_timer_start = True

            self.seen_so_far += bytes_amount   
            if self.seen_so_far >= self.size:
                self.monitor.is_exit = True

class DownloadProgressPercentage(ProgressPercentage):
    '''
        下载进度条类
    '''
    def __init__(self, filename,size,seen_so_far=0): 
        super(DownloadProgressPercentage,self).__init__(filename,self.DOWNLOAD_PROGRESS,seen_so_far)
        self.size = size
        assert(self.size >= 0)

class UploadProgressPercentage(ProgressPercentage):
    '''
        上传进度条
    '''
    def __init__(self, filename,seen_so_far=0): 
        super(UploadProgressPercentage,self).__init__(filename,self.UPLOAD_PROGRESS,seen_so_far)
        self.size = os.path.getsize(filename) 
        assert(self.size >= 0)
