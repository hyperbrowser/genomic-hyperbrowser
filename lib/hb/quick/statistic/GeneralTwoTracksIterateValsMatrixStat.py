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
#from gold.statistic.GeneralTwoTracksIterateValsStat import GeneralTwoTracksIterateValsStat
from quick.statistic.GeneralTwoCatTracksJoinWithDoubleDictSumStat import GeneralTwoCatTracksJoinWithDoubleDictSumStat
from copy import copy

#fixme: Special case, category and join with double dict. Should be made general

class GeneralTwoTracksIterateValsMatrixStat(MagicStatFactory):
    pass

#class GeneralTwoTracksIterateValsMatrixStatSplittable(StatisticSumResSplittable):
#    pass
            
class GeneralTwoTracksIterateValsMatrixStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, rawStatistic, **kwArgs):
        self._rawStatistic = rawStatistic
        Statistic.__init__(self, region, track, track2, rawStatistic=rawStatistic, **kwArgs)
        
    def _getAllSecondLevelKeys(self, res):
        keys2 = set([])
        for key1 in res.keys():
            if res[key1] is not None:
                for key2 in res[key1].keys():
                    keys2.add(key2)
        return keys2
        
    def _compute(self):
        res = self._children[0].getResult()
        keys2 = self._getAllSecondLevelKeys(res)
        cols = [key2 for key2 in keys2]
        row = []
        matrix = []
        for key1 in res.keys():
            row.append(key1)
            matrix.append([res[key1].get(key2) for key2 in res[key1].keys()])
        return {'Matrix': matrix, 'Rows':row ,'Cols':cols}
        
    def _createChildren(self):
        allKwArgs = copy(self._kwArgs)
        allKwArgs.update({'rawStatistic':self._rawStatistic})
        #fixme: switches tracks as of now
        self._addChild(GeneralTwoCatTracksJoinWithDoubleDictSumStat(self._region, self._track2, self._track, **allKwArgs))
