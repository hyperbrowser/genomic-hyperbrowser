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
'''
Created on Nov 3, 2015

@author: boris
'''
from gold.statistic.MCSamplingStat import MCSamplingStatUnsplittable
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.application.SignatureDevianceLogging import takes
from quick.statistic.McFdrSamplingV2Stat import *
from quick.statistic.StatisticV2 import StatisticV2
from quick.util.McEvaluators import *
from quick.statistic.NaiveMCSamplingV2Stat import NaiveMCSamplingV2Stat
from third_party.typecheck import one_of


class RandomizationManagerV3Stat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class RandomizationManagerV3StatSplittable(StatisticSumResSplittable):
#    pass
            
class RandomizationManagerV3StatUnsplittable(StatisticV2):    
    IS_MEMOIZABLE = False

    @takes("RandomizationManagerV3StatUnsplittable", callable, one_of(basestring,type),basestring, one_of(basestring,Statistic))
    def _init(self, evaluatorFunc, mcSamplerClass, tail, rawStatistic, **kwArgs):
        if type(evaluatorFunc) is str:
            evaluatorFunc = globals()[evaluatorFunc]
        self._evaluatorFunc = evaluatorFunc

        if isinstance(mcSamplerClass, basestring):
            mcSamplerClass = globals()[mcSamplerClass]
            assert issubclass(mcSamplerClass, (MCSamplingStatUnsplittable,MagicStatFactory)), (type(mcSamplerClass), mcSamplerClass)
        self._mcSamplerClass = mcSamplerClass
        
        self._tail = tail
        self._rawStatistic = self.getRawStatisticClass(rawStatistic) #just to extract name

    def _compute(self):
        return self._evaluatorFunc( self._children[0].getResult(), self._tail, self.getRawStatisticMainClassName() )
    
    def _createChildren(self):
        self._addChild(self._mcSamplerClass(self._region, self._trackStructure, **self._kwArgs) )

    def getRawStatisticMainClassName(self):
        return self._rawStatistic.__name__.replace('Splittable', '').replace('Unsplittable', '')
        
    @classmethod
    def validateAndPossiblyResetLocalResults(cls, localManagerObjects):
        localSamplingObjects = [x._children[0] for x in localManagerObjects]
        numNonDetermined = localManagerObjects[0]._children[0].validateAndPossiblyResetLocalResults(localSamplingObjects)
        for i in range(len(localSamplingObjects)):
            if not localSamplingObjects[i].hasResult():
                del localManagerObjects[i]._result
        return numNonDetermined

    def validateAndPossiblyResetGlobalResult(self, dummy):
        res = self._children[0].validateAndPossiblyResetGlobalResult(dummy)
        if res[0]==1:
            #print 'TEMP3'
            del self._result
        return res