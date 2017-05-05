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
from gold.origdata.GtrackComposer import StdGtrackComposer
from gold.origdata.TrackGenomeElementSource import TrackViewGenomeElementSource
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.track.TrackFormat import TrackFormatReq
from urllib import quote

from gold.util.CustomExceptions import ShouldNotOccurError
from proto.CommonFunctions import ensurePathExists


class TrackWriterStat(MagicStatFactory):
    pass


class TrackWriterStatSplittable(StatisticSplittable):
    def _combineResults(self):
        self._result = self._childResults[0]
        for childResult in self._childResults:
            if childResult != self._result:
                raise ShouldNotOccurError('All output filenames should be the same.')


class TrackWriterStatUnsplittable(Statistic):
    def _init(self, trackFilePath, **kwArgs):
        self._trackFilePath = trackFilePath

    def _compute(self):
        #TODO: fix this new implementation, it doesn't seem to write the lines yet
        tvGeSource = TrackViewGenomeElementSource('hg19', self._children[0].getResult(), self._track.trackName)
        StdGtrackComposer(tvGeSource).composeToFile(self._trackFilePath)


        # ensurePathExists(self._trackFilePath)
        # outputFile = open(self._trackFilePath, 'a')
        #
        # trackView = self._children[0].getResult()
        # starts = trackView.startsAsNumpyArray()
        # ends = trackView.endsAsNumpyArray()
        #
        # for segmentIndex in range(0, len(starts)):
        #     outputFile.write('\t'.join([self._region.chr, str(starts[segmentIndex]), str(ends[segmentIndex])]) + '\n')
        #
        # outputFile.close()

        # this return is not entirely necessary, as the filenames have already been added to the trackstructure
        return quote(self._trackFilePath)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq()))