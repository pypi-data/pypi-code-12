# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="UShareSoft"

import urllib2
import traceback
from hurry.filesize import size
from progressbar import AnimatedMarker, Bar, BouncingBar, Counter, ETA, \
    FileTransferSpeed, FormatLabel, Percentage, \
    ProgressBar, ReverseBar, RotatingMarker, \
    SimpleProgress, Timer
import printer

class Download():
        
        def __init__(self, url, dest_file_name):
                self.url = url
                self.dest_file_name = dest_file_name

        def chunk_read(self, response, file, chunk_size=8192, report_hook=False):
                # inspired by http://stackoverflow.com/questions/2028517/python-urllib2-progress-hook
                total_size = response.info().getheader('Content-Length').strip()
                total_size = int(total_size)
                bytes = 0

                printer.out("Ready to download "+size(total_size), printer.INFO)

                #widgets = ['Status: ', Percentage(), ' ', Bar('>'), ' ', ETA(), ' ', FileTransferSpeed()]
                widgets = ['Status: ', Percentage(), ' ', Bar('>'), ' ', ETA()]
                self.pbar = ProgressBar(widgets=widgets, maxval=100).start()

                while True:
                        chunk = response.read(chunk_size)
                        file.write(chunk)
                        bytes += len(chunk)
                        if not chunk:
                                break
                        if report_hook:
                                self.progress_update((bytes/chunk_size), chunk_size, total_size)

                return bytes

        def start(self):
                file = open(self.dest_file_name, 'wb')
                try:
                        response = urllib2.urlopen(self.url)
                        bytes = self.chunk_read(response, file, report_hook=True)
                        self.progress_finish()
                except urllib2.HTTPError as e:
                        printer.out("Error getting URL: "+self.url, printer.ERROR)
                        raise e



        def progress_update(self, count, blockSize, totalSize):
                percent=None
                if totalSize-blockSize<=0:
                        percent=50
                else:
                        if totalSize-(count*blockSize)>=0:
                                percent = int(count*blockSize*100/totalSize)
                if percent is not None:
                        self.pbar.update(percent)
                
        def progress_finish(self):
                self.pbar.finish()