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
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy

class ListOfPresentCategoriesStat(MagicStatFactory):
    pass

class ListOfPresentCategoriesStatSplittable(StatisticSplittable):
    def _combineResults(self):
        uniqueSet = set()
        for catSet in self._childResults:
            uniqueSet.update(catSet)

        return uniqueSet

class ListOfPresentCategoriesStatUnsplittable(Statistic):
    def _compute(self):
        return set(numpy.unique(self._children[0].getResult().valsAsNumpyArray()))

        #if catSequence is None:
        #    raise IncompatibleTracksError()
        #
        #catSet = numpy.unique(catSequence)
        #res = {}
        #for cat in catSet:
        #    filter = (catSequence==cat)
        #    if rawData.trackFormat.reprIsDense():
        #        res[cat] = filter.sum()
        #    else:
        #        #print 'BpCoverage..: ',ends, starts, catSequence, catSet, type(catSequence), filter
        #        #res[cat] = ends[filter].sum() - starts[filter].sum()
        #        catStarts = starts[filter]
        #        catEnds = ends[filter]
        #
        #        totCoverage = catEnds.sum() - catStarts.sum()
        #
        #        runningMaxEnds = numpy.maximum.accumulate(catEnds)
        #        tempArray1 = runningMaxEnds[:-1] - catStarts[1:]
        #        tempArray2 = runningMaxEnds[:-1] - catEnds[1:]
        #        totOverlap = tempArray1[tempArray1 > 0].sum() - tempArray2[tempArray2 > 0].sum()
        #
        #        res[cat] = totCoverage - totOverlap
        #
        #return res

    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(val='category', allowOverlaps=True)) )
