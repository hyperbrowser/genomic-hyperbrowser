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
Created on Mar 1, 2016

@author: boris
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.GenericT1T2BinValuesCorrelationStat import GenericT1T2BinValuesCorrelationStat


class T1T2BinValuesCorrelationWithKendallCountStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class T1T2BinValuesCorrelationWithKendallCountStatSplittable(StatisticSumResSplittable):
#    pass
            
class T1T2BinValuesCorrelationWithKendallCountStatUnsplittable(Statistic):    
    def _compute(self):
        return self._children[0].getResult()
    
    def _createChildren(self):
        self._addChild(GenericT1T2BinValuesCorrelationStat(self._region, self._track, self._track2, perBinStatistic='CountStat', corrMethod='kendall'))