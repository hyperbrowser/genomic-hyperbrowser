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
from collections import defaultdict

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable, StatisticSplittable
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from gold.track.TrackFormat import TrackFormatReq
import os
from urllib import quote, unquote

from gold.util.CustomExceptions import ShouldNotOccurError


class TrackWriterStat(MagicStatFactory):
    pass


class TrackWriterStatSplittable(StatisticSplittable): #TODO Lonneke: what kind of splittable statistic is this? it does not have to do anything, maybe make a new kind of splittable statistic?
    def _combineResults(self):
        self._result = self._childResults[0]
        for childResult in self._childResults:
            if childResult != self._result:
                raise ShouldNotOccurError('All output filenames should be the same.')


# de grote vraag die dus nog moet ingevuld worden; hoe wordt het gesplit?
# splitten doet de volgende dingen:
# for region in alle genomeregions (chromosomen)
# maak nieuwe unieke naam
# call unsplittable (track, naam, region)

class TrackWriterStatUnsplittable(Statistic):
    def _init(self, quotedTrackFileName, **kwArgs):
        self._trackFileName = unquote(quotedTrackFileName)

    def _compute(self):
        f = open(self._trackFileName, 'a')
        #print 'FILENAME = ' + self._outFileName

        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        #print os.path.realpath(f.name)

        for segmentIndex in range(0, len(starts)):
            f.write('\t'.join([self._region.chr, str(starts[segmentIndex]), str(ends[segmentIndex])]) + '\n')
            #print '\t'.join([self._region.chr, str(starts[segmentIndex]), str(ends[segmentIndex])])

        f.close()

        # this return is not entirely necessary, as the filenames have already been added to the trackstructure
        return quote(self._trackFileName)

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq()))