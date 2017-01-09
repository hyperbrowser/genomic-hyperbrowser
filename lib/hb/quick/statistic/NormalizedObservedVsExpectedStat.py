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
from gold.statistic.Statistic import MultipleTrackStatistic
from quick.statistic.SummarizedInteractionWithOtherTracksV2Stat import SummarizedInteractionWithOtherTracksV2Stat
from gold.track.TrackStructure import TrackStructure
from quick.util.debug import DebugUtil


class NormalizedObservedVsExpectedStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

#class NormalizedObservedVsExpectedStatSplittable(StatisticSumResSplittable):
#    pass
            
class NormalizedObservedVsExpectedStatUnsplittable(MultipleTrackStatistic):
    """The statistic is normalized in relation to the reference GSuite."""

    def _init(self, queryTracksNum=None, **kwArgs):
        self._queryTracksNum = int(queryTracksNum)

    def _compute(self):
        nominator = self._nominator.getResult()
        denominator = self._denominator.getResult()
        # if nominator and denominator and denominator > 0:
        #     return float(nominator)/denominator
        if nominator is not None and denominator is not None and denominator > 0:
            return float(nominator)/denominator
        else:
            from numpy import nan
            return nan
    
    def _createChildren(self):
        
        ts = TrackStructure()
        ts[TrackStructure.QUERY_KEY] = [self._tracks[0]]
        ts[TrackStructure.REF_KEY] = self._tracks[self._queryTracksNum:]
        # DebugUtil.insertBreakPoint()
        from quick.statistic.StatFacades import ObservedVsExpectedStat
        self._nominator = self._addChild(ObservedVsExpectedStat(self._region, self._track, self._track2, **self._kwArgs))
        self._denominator = self._addChild(
            SummarizedInteractionWithOtherTracksV2Stat(
                self._region,
                ts,
                pairwiseStatistic='ObservedVsExpectedStat',
                summaryFunc='avg',
                reverse=(self._kwArgs['reverse'] if 'reverse' in self._kwArgs else 'No'))
        )