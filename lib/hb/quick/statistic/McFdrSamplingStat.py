# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.

from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.McEvaluators import computeNumMoreExtreme
from quick.statistic.McFdr import McFdr
from gold.util.CommonFunctions import isIter
import numpy
from quick.statistic.SequentialMcSamplingStat import SequentialMcSamplingStatUnsplittable

class McFdrSamplingStat(MagicStatFactory):
    '''
    Samples according to the McFdr scheme,
    relying on validateAndPossiblyResetLocalResults to continue sampling until enough has been sampled
    '''
    pass

class McFdrSamplingStatUnsplittable(SequentialMcSamplingStatUnsplittable):
    def _init(self, fdrThreshold, globalPvalThreshold, **kwArgs):
        self._adjPValue = None
        if isIter(self._region): #to determine whether at global level or not, should find better mechanism to determine..
            self._adjPValueThreshold = float(globalPvalThreshold)
        else:
            self._adjPValueThreshold = float(fdrThreshold)            
        SequentialMcSamplingStatUnsplittable._init(self, **kwArgs)
        
    
    def isMcDetermined(self):
        if self.isIndividuallyMcDetermined():
            return True
        #print 'TEMP2: ', self._region, (numNonExtreme, self._mThreshold, numSamples, self._maxSamples, self._adjPValue, self._adjPValueThreshold)        
        if (self._adjPValue is not None) and (self._adjPValueThreshold is not None) and \
            (not numpy.isnan(self._adjPValue)) and (self._adjPValue<self._adjPValueThreshold):
            #print 'TEMP4', (self._adjPValue<self._adjPValueThreshold), (self._adjPValue, self._adjPValueThreshold)
            return True
        
        return False
        
    @classmethod
    def validateAndPossiblyResetLocalResults(cls, localSamplingObjects):
        #to load r libraries for McFdr:
        McFdr._initMcFdr()

        numNonDetermined = 0
        pvals = [x._getPval() for x in localSamplingObjects]
        qValues = McFdr.adjustPvalues(pvals, verbose=False)
        #First decide whether any further sampling will be needed (whether numNonDetermined==0)
        for i in range(len(localSamplingObjects)):
            localSamplingObjects[i]._adjPValue = qValues[i]
            if not localSamplingObjects[i].isMcDetermined():
                numNonDetermined +=1
                
        #print 'TEMP3: ', numNonDetermined
        if numNonDetermined>0:
            #Decide which will need further sampling (through deleting result), based on individualMcDetermined
            for i in range(len(localSamplingObjects)):
                if not localSamplingObjects[i].isIndividuallyMcDetermined():
                    del localSamplingObjects[i]._result
        return numNonDetermined
        
    def validateAndPossiblyResetGlobalResult(self, dummy):
        self._adjPValue = self._getPval()
        determined = self.isMcDetermined()
        if not determined:
            #print 'TEMP4'
            del self._result
        
        numSamples = len(self._mcSamples)
        numNonExtreme = numSamples - computeNumMoreExtreme(self._realSample, self._mcSamples, self._tail)
        #print 'TEMP1: ', [0 if determined else 1, numNonExtreme, self._mThreshold, self._adjPValue, self._adjPValueThreshold]
        return [0 if determined else 1, numNonExtreme, self._mThreshold, self._adjPValue, self._adjPValueThreshold]
