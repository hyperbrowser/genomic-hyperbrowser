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
from gold.util.CommonFunctions import getClassName

class GenericResultsCombinerStat(MagicStatFactory):
    pass

#class GenericResultsCombinerStatSplittable(StatisticSumResSplittable):
#    pass
            
class GenericResultsCombinerStatUnsplittable(Statistic):
    def _init(self, rawStatistics=[], **kwArgs):
        if isinstance(rawStatistics, basestring):
            from gold.statistic.AllStatistics import STAT_CLASS_DICT
            
            rawStatistics = [STAT_CLASS_DICT[rawStat] for rawStat in rawStatistics.split('^')]
        self._rawStatistics = rawStatistics
        
        if not hasattr(self, '_track2'):
            self._track2 = None #to allow track2 to be passed on as None to rawStatistics without error. For use by single-track statistics
        
    def _compute(self):
        from collections import OrderedDict
        #res = {}
        res = OrderedDict()
        for childStat in self._children:
            childRes = childStat.getResult()
            #print '1',str(self._region), str(childRes)
            if not isinstance(childRes, dict):
                childRes = {getClassName(childStat).replace('Unsplittable','').replace('Splittable',''):childRes}
            #print '2',str(self._region), str(childRes)
            for key in childRes:
                assert not key in res
                res[key] = childRes[key]
            #print '3',str(self._region), str(res)
            #res.update(  childRes)
        return res
    
    def _createChildren(self):
        for rawStat in self._rawStatistics:
            self._addChild( rawStat(self._region, self._track, self._track2, **self._kwArgs) )
