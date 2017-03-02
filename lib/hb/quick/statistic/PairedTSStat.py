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
    def _init(self, rawStatistic, **kwArgs):
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)

    def _compute(self):
        ts = self._trackStructure._copyTreeStructure()
        ts.results = self._children[0].getResults()
        return ts

    def _createChildren(self):
        assert self._trackStructure.isPairedTs() #TODO: Should PairedTS be a subclass of TrackStructure
        t1 = self._trackStructure['query']
        t2 = self._trackStructure['reference']
        self.addChild(self._rawStatistic(self._region, t1, t2))
