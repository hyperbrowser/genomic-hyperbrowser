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
from gold.origdata.GenomeElement import GenomeElement
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import MultipleTrackStatistic
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
from quick.statistic.RawOverlapSortedStartEndCodedEventsStat import RawOverlapSortedStartEndCodedEventsStat
from numpy import array


class UnionTrackOfGSuiteTracksStat(MagicStatFactory):
    """
    Generate a track that represents the union of all the tracks in the GSuite
    """
    pass


#class UnionTrackOfGSuiteTracksStatSplittable(StatisticSumResSplittable):
#    pass


class UnionTrackOfGSuiteTracksStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        tv1 = self._children[0].getResult()
        allSortedCodedEvents = self._children[1].getResult()

        allEventCodes = (allSortedCodedEvents % 4) - 2

        allSortedDecodedEvents = allSortedCodedEvents / 4

        from numpy.ma import add
        cumulativeCoverStatus = add.accumulate(allEventCodes)
        assert len(cumulativeCoverStatus) == len(allSortedDecodedEvents), str(len(allSortedDecodedEvents))

        unionStartList = []
        unionEndList = []

        startedFlag = False
        for i, cumVal in enumerate(cumulativeCoverStatus):
            if cumVal == 1 and not startedFlag:
                startPos = allSortedDecodedEvents[i]
                startedFlag = True
            elif cumVal == 0:
                if startPos:
                    unionStartList.append(startPos)
                    unionEndList.append(allSortedDecodedEvents[i])
                    startPos = None
                    startedFlag = False


        return [GenomeElement(start=x, end=y) for x, y in zip(unionStartList, unionEndList)]

        # return TrackView(genomeAnchor=tv1.genomeAnchor, startList=array(unionStartList),
        #                  endList=array(unionEndList), valList=None,
        #                  strandList=None, idList=None, edgesList=None,
        #                  weightsList=None, borderHandling=tv1.borderHandling,
        #                  allowOverlaps=False)


    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False)))
        self._addChild(RawOverlapSortedStartEndCodedEventsStat(self._region, self._track, self._track2, **self._kwArgs))


