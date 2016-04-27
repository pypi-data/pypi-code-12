'''
Created on Dec 9, 2013
@author: dazhe.meng

New permute class
'''

import numpy as np
import random
import logging
logger = logging.getLogger('gwaportalpipeline.enrichment')

class permute():
    def __init__(self):
        pass
    
    def load_vectors(self, target, match):
        ' load input as 0,1 vectors with length equal to total number of snps '
        self.target = target
        self.match = match
        if self.target.shape != self.match.shape:
            raise ValueError('Non matching number of snps')
        
    def rotate_and_count(self, step):
        ' Do one set of rotation and count number of matches'
        if step == 0:
            return np.sum(self.target*self.match)
        else:
            testtarget = np.hstack((self.target[step:],self.target[:step]))
            return np.sum(testtarget*self.match)
        
    def permute_p_val(self, num):
        ' Do multiple rotations to obtain a p-value '
        originalmatch = self.rotate_and_count(0)
        num_reach_original = 0
        randomset = random.sample(xrange(1,self.target.shape[0]), num)
        num = float(num)
        for ix,step in enumerate(randomset):
            if ix % (num / 10) == 0:
                logger.info('Permutation %s/%s' % (ix,num),extra={'progress':(5 + ix/num*95)})
            if self.rotate_and_count(step)>=originalmatch:
                num_reach_original += 1
        return float(num_reach_original)/num
        
