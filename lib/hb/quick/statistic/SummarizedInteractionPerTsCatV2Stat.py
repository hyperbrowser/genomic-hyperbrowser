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
from quick.statistic.StatisticV2 import StatisticV2
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from gold.track.TrackStructure import TrackStructureV2


class SummarizedInteractionPerTsCatV2Stat(MagicStatFactory):
    """
    
    """
    pass


#class SummarizedInteractionPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass


class SummarizedInteractionPerTsCatV2StatUnsplittable(StatisticV2):
    def _compute(self):
        ts = TrackStructureV2()
        for cat in self._catResults:
            ts[cat] = self._catResults[cat].getResult()
        return ts

    def _createChildren(self):
        reRootedTS = self._trackStructure.makeTreeSegregatedByCategory( self._trackStructure['reference'])
        self._catResults = {}
        for cat, catTS in reRootedTS.iteritems():
            self._catResults[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, **self._kwArgs))