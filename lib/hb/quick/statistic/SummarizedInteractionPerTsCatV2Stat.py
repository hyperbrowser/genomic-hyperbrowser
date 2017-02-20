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


class SummarizedInteractionPerTsCatV2Stat(MagicStatFactory):
    """
    
    """
    pass


#class SummarizedInteractionPerTsCatV2StatSplittable(StatisticSumResSplittable):
#    pass


class SummarizedInteractionPerTsCatV2StatUnsplittable(StatisticV2):
    def _compute(self):
        #self._reRootedTS.result = self._catSummaryFunc([catTS.result for catTS in self._reRootedTS.values()])
        #self._reRootedTS.summarizeChildResults(summaryFunc)
        #return self._reRootedTS
        result = summaryFunc([catChild.getResult() for catChild in self._catChildren])
        raise


    def _createChildren(self):
        #self._catResults = {}
        self._reRootedTS = self._trackStructure.reRoot( self._trackStructure['ref'])
        for cat, catTS in self._reRootedTS.iteritems():
            #self._catChildren[cat] = self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, self._kwArgs))
            self._addChild(SummarizedInteractionWithOtherTracksV2Stat(self._region, catTS, self._kwArgs))