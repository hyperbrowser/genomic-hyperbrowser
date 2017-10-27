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
from quick.statistic.GenericRelativeToGlobalStat import GenericRelativeToGlobalStat, GenericRelativeToGlobalStatUnsplittable
from quick.statistic.GenericRelativeToGlobalV2Stat import GenericRelativeToGlobalV2Stat, \
    GenericRelativeToGlobalV2StatUnsplittable
from quick.statistic.StatisticV2 import StatisticV2, StatisticV2Splittable
from gold.statistic.CountElementStat import CountElementStat
from quick.statistic.SummarizedStat import SummarizedStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError


class PairedTSStat(MagicStatFactory):
    """
    """
    pass


class PairedTSStatUnsplittable(StatisticV2):

    PROGRESS_COUNT = 1

    def _init(self, pairedTsRawStatistic, progressPoints=None, progressStyle='html', **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(pairedTsRawStatistic)
        self._progressPoints = progressPoints
        self._progressStyle = progressStyle

    def _compute(self):
        ts = self._trackStructure._copyTreeStructure()
        ts.result = self._children[0].getResult()
        self._printProgress()
        return ts

    def _printProgress(self):
        if self._progressPoints:
            if PairedTSStatUnsplittable.PROGRESS_COUNT == 1:
                if self._progressStyle == 'html':
                    print '<br>'
                    print "<p>Progress output (expected points: %s)</p>" % self._progressPoints
                else:
                    print
                    print "Progress output (expected points: %s)" % self._progressPoints
            print ".",
            if PairedTSStatUnsplittable.PROGRESS_COUNT % 100 == 0:
                print PairedTSStatUnsplittable.PROGRESS_COUNT
                if self._progressStyle == 'html':
                    print '<br>'
            PairedTSStatUnsplittable.PROGRESS_COUNT += 1

    def _createChildren(self):
        assert self._trackStructure.isPairedTs() #TODO: Should PairedTS be a subclass of TrackStructure?
        t1 = self._trackStructure['query'].track
        t2 = self._trackStructure['reference'].track
        self._addChild(self._rawStatistic(self._region, t1, t2, **self._kwArgs))
