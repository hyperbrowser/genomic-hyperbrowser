'''
Created on Nov 3, 2015

@author: boris
'''
from gold.statistic.MCSamplingStat import MCSamplingStatUnsplittable
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.application.SignatureDevianceLogging import takes
from quick.statistic.GenericMCSamplesV2Stat import GenericMCSamplesV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from third_party.typecheck import one_of


class NaiveMCSamplingV2Stat(MagicStatFactory):
    '''
    Just computes a pre-specified number of MC samples (of the test statistic),
    and a test statistic on the real data,
    and returns these
    '''
    pass

class NaiveMCSamplingV2StatUnsplittable(MCSamplingStatUnsplittable):
    @takes('NaiveMCSamplingV2StatUnsplittable',Statistic, one_of(basestring,int))
    def _init(self, rawStatistic, maxSamples, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)
        if kwArgs.get('minimal') == True:
            self._maxSamples = 1
        else:
            self._maxSamples = int(maxSamples)
        assert not 'numMcSamples' in kwArgs, kwArgs #numMcSamples should be determined based on maxSamples and passed on, not specified directly
        
    def _compute(self):
        return (self._realTestStatistic.getResult(), self._mcTestStatistics.getResult())
    
    def _createChildren(self):
        self._realTestStatistic = self._addChild(self._rawStatistic(self._region, self._trackStructure, **self._kwArgs) )
        self._mcTestStatistics = self._addChild(GenericMCSamplesV2Stat(self._region, self._trackStructure, numMcSamples=self._maxSamples, **self._kwArgs) )
        
    def isMcDetermined(self):
        return True #only needs to be called once
