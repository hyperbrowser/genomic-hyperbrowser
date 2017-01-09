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
from gold.statistic.Statistic import Statistic
#from proto.RSetup import r
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import IncompatibleAssumptionsError
from collections import OrderedDict

class SimpleFunctionCorrelationPvalStat(MagicStatFactory):
    pass

#class SimpleFunctionCorrelationPvalStatSplittable(StatisticSumResSplittable):
#    pass
            
class SimpleFunctionCorrelationPvalStatUnsplittable(Statistic):    
    def __init__(self, region, track, track2, method='pearson', tail='different', **kwArgs):
        assert method in ['pearson','spearman','kendall']
        assert tail in ['more', 'less', 'different']
        tailMapping = {'more': "greater", 'less': "less", 'different': "two.sided"}
        
        self._method = method
        self._rTail = tailMapping[tail]
        Statistic.__init__(self, region, track, track2, method=method, tail=tail, **kwArgs)

    def _checkAssumptions(self, assumptions):
        if not assumptions == 'preserveBoth':
            raise IncompatibleAssumptionsError
    
    def _compute(self):        
        x = self._children[0].getResult().valsAsNumpyArray()
        y = self._children[1].getResult().valsAsNumpyArray()
        if len(x)<2 or len(y)<2:
            pval = None
            testStat = None
        else:
            from proto.RSetup import r

            #rpy1
            #xAsR = r.unlist([float(num) for num in x])
            #yAsR = r.unlist([float(num) for num in y])
            #corTestRes = r('cor.test')(xAsR, yAsR, alternative=self._rTail, method=self._method)
            
            corTestRes = r('cor.test')(x, y, alternative=self._rTail, method=self._method)
            pval = corTestRes.rx2(3) #should be rx("p.value")
            testStat = corTestRes.rx2(1) #should be rx("statistic")
            
        return OrderedDict([ ('P-value', pval), ('Test statistic: ' + self._method, testStat)])
    
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='number', dense=True)) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(val='number', dense=True)) )
