# -*- coding: utf-8 -*-
import cv2

import numpy as np

from scipy.optimize import curve_fit
from scipy.signal import argrelextrema
from scipy.ndimage.filters import median_filter, gaussian_filter
from scipy.misc import factorial

from fancytools.os.PathStr import PathStr



def gauss(x,  a, b, c, d=0):
    '''
    a -> height of the curve's peak
    b -> position of the center of the peak
    c ->  standard deviation or Gaussian RMS width
    d -> offset
    '''
    return a * np.exp(  -(((x-b)**2 )  / (2*(c**2)) ) ) + d 


#TODO: embedd:
def poisson(x, a, b, c, d=0):
    '''
    Poisson function
    a -> height of the curve's peak
    b -> position of the center of the peak
    c ->  standard deviation 
    d -> offset
    '''
    lamb = 1
    X = (x/(2*c)).astype(int)
    return a * (( lamb**X/factorial(X)) * np.exp(-lamb) ) +d



class FitHistogramPeaks(object):
    '''
    try to fit the histogram of an image as an addition of 2 GAUSSian distributions
    stores the position the the peaks in self.fitParams
    '''
    
    def __init__(self, img, 
                 binEveryNPxVals=10, 
                 fitFunction=gauss,
                 minNPeaks=2,
                 peaks_added_up=True,
                 stop_after_peak=None,
                 debug=False,
                 gaussian_filter_sigma=None,
                 exclude_small_peaks=True):
        '''
        peaks_added_up - if True, than histogram is built by sum of 
             all peaks (connection is AND instead of OR)
             
        exclude_small_peaks - exclude all peaks additional to [minNPeaks]
                              if they are much smaller
        '''
        self.fitFunction = fitFunction
        
        #TODO: remove yvals2 - no smoothing any more
        ##########################################
        
        
        #OPEN IMAGE
        self.img = img
        if isinstance(img, basestring):
            self.img = cv2.imread(img, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_GRAYSCALE)
        if self.img is None:
            raise Exception("image doesn't exist")
        #remove erroneous pixels
        self.img_med = median_filter(self.img, 3)
        #CREATE HISTOGRAM
        mnImg = np.min(self.img_med)
        mxImg = np.max(self.img_med)
        #one bin for every  N pixelvalues
        nBins = int( ( mxImg - mnImg)  / binEveryNPxVals )
        if nBins < 50:
            nBins = 50
        elif nBins > 200:
            nBins = 200
        #print nBins, mnImg, mxImg
        self.yvals, bin_edges = np.histogram(self.img, bins=nBins, range=(mnImg, mxImg))
        self.yvals = np.asfarray(self.yvals)
        #remove small values
#         self.yvals[self.yvals<np.max(self.yvals)*5e-4]=0
        #bin edges give start and end of an area-> move that to the middle:
        self.xvals = bin_edges[:-1]+np.diff(bin_edges)*0.5
        

        #TODO: find proper equation to determine smoothing factor
        if gaussian_filter_sigma is None:
            if nBins == 200:
                gaussian_filter_sigma = 5
            elif nBins > 100:
                gaussian_filter_sigma = 3
            else:
                gaussian_filter_sigma = 2

        self.yvals2 = gaussian_filter(self.yvals, gaussian_filter_sigma)

        #yused = self.yvals2

        def getExtrema(y):
            xpeak = argrelextrema(y, np.greater, mode='wrap')[0]
            xlow = argrelextrema(y, np.less_equal, mode='wrap')[0]
            return xpeak, xlow

        #LOCAL MAXIMA/MINIMA:
        xpeak, xlow = getExtrema(self.yvals)

        #if len(xpeak) < minNPeaks:
            #yused = self.yvals
            #print "couln't find %s peaks from smoothed histogram" %minNPeaks
            #only one peak found: use unsmoothed vals
            #xpeak, xlow = getExtrema(yused)
        if len(xpeak) < minNPeaks:
            raise Exception("couln't find %s peaks from histogram" %minNPeaks) 
        xlow = self._filterConsecutiveValues(xlow)
        xlow = self._completeXlow(xlow, xpeak, self.yvals)

        #PEAK POSITIONS TO FIT GAUSSIANS INBETWEEN
        #peakPos = [ [min,max,min-position],[]...]
        peakPos = np.append(xpeak, xlow)
        peakPos.sort()

        peakPos = self._filterPeaks(peakPos, minNPeaks)
        peakPos = self._reshapePeakspos(peakPos)

    
        #REMOVE???
        if exclude_small_peaks:
            #remove all peaks smaller than half
            #of the second smallest peak
            yp = self.yvals[peakPos[:,1]]
            #index of n highest value:
            i = np.argpartition(yp, -minNPeaks)[-minNPeaks]
            ind = yp > yp[i]/2
            peakPos = peakPos[ind]

        
        if debug:
            print 'found %s peaks' %len(peakPos)

        self.yvals_orig = self.yvals.copy()
        self.yvals2_orig = self.yvals2.copy()

        #FIT FUNCTION TO EACH PEAK
        self.fitParams = []
        for n,p in enumerate(peakPos):
            #local value range:
            yvals = self.yvals[p[0]:p[2]]
            #yvals2 = self.yvals2[p[0]:p[2]]
            xvals = self.xvals[p[0]:p[2]]
            print xvals,888888888888
            
            i = np.argmax(yvals)
            #peak position/value:
            xp = xvals[i]
            yp = yvals[i]
            #standard deviation:
            sigma = (xvals[-1]-xvals[0])/2
            
            print n,p,yp,xp,6666666666666
            
            
            #if 1st, last peaks are at border:
            if i == 0:
                sigma/=2
            if i+p[0] == len(self.xvals):
                sigma/=2
  
            init_guess = (yp,xp,sigma)
            
#             def fn(fitFn, x, y, x0):
#                 y_fit = self.fitFunction(x)
#                 dy = 
#                 
#                 y_fit = curve_fit(self.fitFunction, xvals, y, 
#                                     p0=init_guess,
#                                     sigma=np.ones(shape=xvals.shape)*1e-8
#                                     )
            
            fn  = lambda y: curve_fit(self.fitFunction, xvals, y, 
                                    p0=init_guess,
                                    sigma=np.ones(shape=xvals.shape)*1e-8
                                    )
            #FIT
            try:
                #fitting procedure using initial guess
                params, _ = fn(yvals)   
            except RuntimeError:
                #couln't fit curve -> try again on smoothed values:
                #try:
                    #params, _ = fn(yvals2)
                #except RuntimeError:  
                if debug:
                    print "couln't fit gaussians -> result will will inaccurate"
                #stay with initial guess: 
                params = init_guess
            except TypeError:

                #couldn't fit maybe because to less values were given
                continue
            
            #if peak is within the image histogram and not too high:
            if (
                #params[0]<2.5*yp and
                (params[1]+2*params[2]> mnImg 
                or params[1]-2*params[2]<mxImg) ):
#             if mnImg < params[1] < mxImg:
                #negative standard deviation is possible...
                params = list(params)
                params[2]  = np.abs(params[2])
                
                self.fitParams.append(params)
                
                if stop_after_peak == len(self.fitParams):
                    #speed up, in case one is only interested if e.g. the background peak
                    return

            if peaks_added_up:
                #if yvals build by gauss ADDEN TOGETHER:
                y = self.fitFunction(self.xvals,*params)
                self.yvals -= y
                self.yvals2 -= y
            
#         self.plotFitResult()
   
    @staticmethod
    def _reshapePeakspos(peakPos):
        endPeakIndices = range(2,len(peakPos),2)[:-1]
        endPeakValues = peakPos[2::2][:-1]
        peakPos = np.insert(peakPos, endPeakIndices,endPeakValues)
        return peakPos.reshape(len(peakPos)/3,3)



    @staticmethod
    def _completeXlow(xlow, xpeak, yvals):
        #COMPLETE MINIMA, so first and last extreme value is minimum
        if xlow[0] > xpeak[0]:
            if xpeak[0] == 0:
                pass
                #xpeak = xpeak[1:]
            else:
                #first local minimum comes later than first lo.max:
                    #add first low val:
                y0=yvals[0]
                for n, y in enumerate(yvals[1:]):
                    if y > y0:
                        break
                    y0=y
                if n > xpeak[0]:
                    n = xpeak[0]
                xlow = np.insert(xlow,0,n)
        if xlow[-1] < xpeak[-1]:
            #add last low val
            y0=yvals[-1]
            for n, y in enumerate(yvals[::-1]):
                if y > y0:
                    break
                y0=y
            xlow = np.append(xlow,len(yvals)-n)
        return xlow



    def _filterConsecutiveValues(self, xlow):
        '''
        filter consecutive values in a list leaving only the middle value:
        in ->  [1, 3, 4, 5, 7, 9]
        out -> [1,    4,    7, 9]
        '''
        if len(xlow) > 1:
            consec = np.diff(xlow) == 1
            indices = np.ones(shape=len(xlow), dtype=bool)
            foundConsec = False
            for n,c in enumerate(consec):
                if not foundConsec and c:
                    foundConsec = True
                    begin = n
                if foundConsec:
                    if c:
                        indices[n] = False 
                    else:
                        middle = (begin + n) / 2
                        indices[middle] = True
                        foundConsec = False
            xlow = xlow[indices]
        return xlow


    def _filterPeaks(self, peakPos, minNPeaks):
        #REMOVE DUPLICATES
        peakPos = np.unique(peakPos)

        if peakPos[0]==0:
            #starts with peak at pos 0
            if self.yvals2[peakPos[0]] > self.yvals2[peakPos[1]]:
                #dd = np.diff(self.yvals[0:5])          
                #if dd[0] < 10 * dd[1:].mean():
                if self.yvals[0] > 5*self.yvals[1:3].mean():
                    #this is an erroneous peak, which is
                    #common after lens distortion removal where background 
                    #values are much higher than 0 but empty places are
                    #replaced with it
                    peakPos = peakPos[1:]
                else:
                    #add another 0 in order to start with with valley: 
                    peakPos = np.insert(peakPos, 0,0)    

        #ONLY APPLY DIFFERENCE FILTER IS THERE ARE MORE PEAKS THAN NEEDED:
        nPeaks = len(peakPos)-2 #remove borders
        nPeaks -= nPeaks / 2  #remove sinks

        if nPeaks <=minNPeaks:
            return peakPos
        
        #FILTER PEAKS from small local variations
        #saying a peaks end only if at least half the amount down after it went up
        diff  = np.diff(self.yvals2[peakPos])
        if diff[0] == 0:
            #in case first peak is at border
            diff[0] = -diff[1]
        
        invalid = []

        end_reached = True
        for n,d in enumerate(diff):
            if end_reached:
                up = d
                down = 0
                end_reached = False
            else:
                down += d                    
                if -down >= 0.25*up:
                #end of peak reached - next peak to start
                    end_reached = True
                else:
                    invalid.append(n)
            
        if not end_reached and len(invalid):
            invalid.pop(-1)
        
        peakPos = np.delete(peakPos, invalid)

        return peakPos


    def fitValues(self, xvals=None):
        if xvals is None:
            xvals = self.xvals
        return [self.fitFunction(xvals,a, b, c) for (a,b,c) in self.fitParams]
        
        
    def plotFitResult(self, show_legend=True, show_plots=True, limitXRangeGaussPlots=True, save_to_file=False, foldername='', filename='', filetype='png'):
        from matplotlib import pyplot
        a,b,c = self.fitParams[-1]
        if limitXRangeGaussPlots:
            #limit x range:

            border = b+3*c
            #find index of xvals outside the border
            for n,x in enumerate(self.xvals):
                if x > border:
                    break 
        else:
            n = None

        xvals = self.xvals[:n]
        yvals = self.yvals_orig[:n]
        yvals2 = self.yvals2_orig[:n]
        
        fit  = self.fitValues(xvals)

        fig, ax = pyplot.subplots(1)

        ax.plot(xvals, yvals, label='histogram')
        ax.plot(xvals, yvals2, label='gauss filtered')

        for n,f in enumerate(fit):
            ax.plot(xvals, f, label='%sst peak' %n)

        l2 = ax.legend(loc='upper center', bbox_to_anchor=(0.7, 1.05),
          ncol=3, fancybox=True, shadow=True)
        l2.set_visible(show_legend)
        
        pyplot.xlabel('pixel value')
        pyplot.ylabel('number of pixels')
        
        if save_to_file:
            p = PathStr(foldername).join(filename).setFiletype(filetype)
            pyplot.savefig(p)
            with open(PathStr(foldername).join('%s_params.csv' %filename), 'w') as f:
                f.write('#x, #y, #ygauss, #fit\n')
                for n, (x,y,ys) in enumerate(zip(xvals,yvals, yvals2)):
                    fstr = ', '.join(str(f[n]) for f in fit)
                    f.write('%s, %s, %s, %s\n' %(x,y,ys,fstr))
            
        if show_plots:
            pyplot.show()





def plotSet(imgDir, posExTime, outDir, show_legend, show_plots, save_to_file, ftype):
    '''
    creates plots showing both found GAUSSIAN peaks, the histogram, a smoothed histogram 
    from all images within [imgDir] 
    
    posExTime - position range of the exposure time in the image name e.g.: img_30s.jpg -> (4,5)
    outDir - dirname to save the output images
    show_legend - True/False
    show_plots - display the result on screen
    save_to_file - save the result to file
    ftype - file type of the output images
    '''
    from matplotlib import pyplot

    xvals = []
    hist = []
    smoothedHist = []
    peaks = []
    exTimes = []
    max_border = 0

    if not imgDir.exists():
        raise Exception("image dir doesn't exist")
    xvals = []

    for n,f in enumerate(imgDir):
        print f
        try:
        #if imgDir.join(f).isfile():
            img = imgDir.join(f)
            s = FitHistogramPeaks(img)
            xvals.append(s.xvals)
            hist.append(s.yvals)
            smoothedHist.append(s.yvals2)
            peaks.append(s.fitValues())
            
            if s.border() > max_border:
                max_border = s.plotBorder()
                
            exTimes.append(float(f[posExTime[0]:posExTime[1]+1]))
        except:
            pass
    nx = 2
    ny = int(len(hist)/nx) + len(hist) % nx

    fig, ax = pyplot.subplots(ny,nx)
    
    #flatten 2d-ax list:
    if nx > 1:
        ax = [list(i) for i in zip(*ax)] #transpose 2d-list
        axx = []
        for xa in ax:
            for ya in xa:
                axx.append(ya)
        ax = axx
    
    for x,h,s,p,e, a in zip(xvals, hist,smoothedHist,peaks, exTimes, ax):

        a.plot(x, h, label='histogram')
        l1 = a.plot(x, s, label='smoothed')
        for n,pi in enumerate(p):
            l2 = a.plot(x, pi, label='peak %s' %n)
        a.set_xlim(xmin=0, xmax=max_border)
        a.set_title('%s s' %e)
        
        pyplot.setp([l1,l2], linewidth=2)#, linestyle='--', color='r')       # set both to dashed

 
    l1 = ax[0].legend()#loc='upper center', bbox_to_anchor=(0.7, 1.05),
    l1.draw_frame(False)


    pyplot.xlabel('pixel value')
    pyplot.ylabel('number of pixels')
    
    fig = pyplot.gcf()
    fig.set_size_inches(7*nx, 3*ny)
    
    if save_to_file:
        p = PathStr(outDir).join('result').setFiletype(ftype)
        pyplot.savefig(p, bbox_inches='tight')
        
    if show_plots:
        pyplot.show()




if __name__ == '__main__':
    imgs =  PathStr('').join('media', 'electroluminescence').all()

    #imgs = ['C:\\Users\\elkb4\\Desktop\\PhD\\Measurements\\EL round robin\\HULC el round robin\\mod2\\corrected\\100_sharp.png']


    for i in imgs:
        f = FitHistogramPeaks(i, minNPeaks=1,binEveryNPxVals=5)
        print f.fitParams
        f.plotFitResult(limitXRangeGaussPlots=True, save_to_file=False)


           
            