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

from collections import OrderedDict
from numpy import median

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.SegmentDistancesStat import SegmentDistancesStat


class MinMaxMedianSegmentDistancesStat(MagicStatFactory):
    pass

class MinMaxMedianSegmentDistancesStatUnsplittable(Statistic):

    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps
    
    def _compute(self):
        dists = self._children[0].getResult()['Result']
        if len(dists) == 0:
                return OrderedDict([('MinDist', 0),('MaxDist', 0), ('MedianDist', 0.0)])

        return OrderedDict([('MinDist', min(dists)),('MaxDist', max(dists)), ('MedianDist', median(dists))])

            
    def _createChildren(self):
        self._addChild( SegmentDistancesStat(self._region, self._track) )
