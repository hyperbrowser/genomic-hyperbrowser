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
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class StrandsInsideBinStat(MagicStatFactory):
    pass

#class MostCommonCategoryStatSplittable(StatisticConcatNumpyArrayResSplittable, OnlyGloballySplittable):
#    IS_MEMOIZABLE = False

class StrandsInsideBinStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        tv1 = self._children[0].getResult()
        strands = tv1.strandsAsNumpyArray()
        if strands is None:
            return None
        strandsUnique = numpy.unique(strands)
        return ''.join(['+' if el == True else ('-' if el == False else '.') for el in strandsUnique])
        #return '+' if True in strandsUnique else '' + '-' if False in strandsUnique else ''
        
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=True) ) )
        