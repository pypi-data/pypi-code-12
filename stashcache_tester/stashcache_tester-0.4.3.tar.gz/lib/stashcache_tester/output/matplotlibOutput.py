import logging

from stashcache_tester.output.generalOutput import GeneralOutput
import numpy
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

from stashcache_tester.util.Configuration import get_option

class MatplotlibOutput(GeneralOutput):
    def __init__(self, sitesData):
        GeneralOutput.__init__(self, sitesData)
        
        
    def startProcessing(self):
        """
        This function will create plots using python's `matplotlib <http://matplotlib.org/index.html>`_.  Currently, it will make:
        
        1. A `violin plot <https://en.wikipedia.org/wiki/Violin_plot>`_ of the distribution of download times for each site given in :ref:`sitesData <sitesData-label>`.
        
        A violin plot example:
        
        .. image:: images/matploblib-violinplot.png
            :width: 300pt
        
        """
        logging.debug("Starting processing with matplotlib...")
            
        # Make a violin plot
        downloadTimes = {}
        for site in self.sitesData:
            siteTimes = self.sitesData[site]
            
            downloadTimes[site] = []
            
            for time in siteTimes:
                downloadTimes[site].append(float(time['duration']))
            
            testsize = get_option("raw_testsize")
            downloadTimes[site] = (float(testsize*8) / (1024*1024)) / numpy.array(downloadTimes[site])
            
            
        plt.violinplot(downloadTimes.values())
        plt.xticks(range(1, len(downloadTimes.keys())+1), downloadTimes.keys())
        plt.ylabel("Mb per second")
        plt.xlabel("Site")
        plt.title("Violin Plot of StashCache Transfer Speeds per Site")
        plt.savefig("violinplot.png")
        plt.clf()
            
        
        
        
        
        
