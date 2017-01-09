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
from gold.statistic.DerivedOverlapStat import DerivedOverlapStat

class OverlapEnrichmentBasedDistanceStat(MagicStatFactory):
    pass

class OverlapEnrichmentBasedDistanceStatUnsplittable(Statistic):
    def _createChildren(self):
        self._addChild( DerivedOverlapStat(self._region, self._track, self._track2) )
        
    def _compute(self):
        derivedOverlap = self._children[0].getResult()
        try:
            averagedEnrichment = (derivedOverlap['1in2'] + derivedOverlap['2in1']) / 2.0
        except: #if None returned from derivedOverlap
            return 1.0
        
        return 1.0/(1 + averagedEnrichment)