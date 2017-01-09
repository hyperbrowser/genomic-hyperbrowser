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
from quick.statistic.BinSizeStat import BinSizeStat
from quick.statistic.RawRipleysKChrStat import RawRipleysKChrStat

#from quick.statistic.SegmentDistancesStat import SegmentDistancesStat

class RipleysKChrStat(MagicStatFactory):
    pass

class RipleysKChrStatUnsplittable(Statistic):
    #IS_MEMOIZABLE = False
    
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #
    #@repackageException(Exception, ShouldNotOccurError)    
    def _compute(self):
        rawK = self._children[0].getResult()
        numBps = self._children[1].getResult()
        import numpy
        if numpy.isnan(rawK):
            return numpy.nan
        else:
            return numBps * rawK
    
    def _createChildren(self):
        self._addChild( RawRipleysKChrStat(self._region, self._track, **self._kwArgs) )
        self._addChild( BinSizeStat(self._region, self._track) )
        #self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=True, \
        #                                                                      allowOverlaps = (self._withOverlaps == 'yes') ) ) )
