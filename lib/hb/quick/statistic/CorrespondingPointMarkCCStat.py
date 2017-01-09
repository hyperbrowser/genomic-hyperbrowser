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
from gold.statistic.NearestPointDistsStat import NearestPointDistsStatUnsplittable
from gold.statistic.NearestPointMarkDiffStat import NearestPointMarkDiffStatUnsplittable
from quick.statistic.CommonStatisticalTests import pearsonCC

class CorrespondingPointMarkCCStat(MagicStatFactory):
    pass

#class CorrespondingPointMarkCCStatSplittable(StatisticSumResSplittable):
#    pass
            
class CorrespondingPointMarkCCStatUnsplittable(NearestPointMarkDiffStatUnsplittable):    
    def _compute(self):
        pairs = [x for x in NearestPointDistsStatUnsplittable._compute(self) if x is not None]
        if len(pairs) == 0:
            return None
        else:
            return pearsonCC( *zip( pairs ) )


    @staticmethod
    def _getObservator(p1, p2):
        return (p1.val(), p2.val()) if (p2 != None and p1.start() == p2.start()) else None
    
