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
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic, StatisticSumResSplittable
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from gold.track.TrackFormat import TrackFormatReq
import os

class TrackWriterStat(MagicStatFactory):
    pass


class TrackWriterStatSplittable(StatisticSumResSplittable): #TODO Lonneke: what kind of splittable statistic is this? it does not have to do anything, maybe make a new kind of splittable statistic?
    pass


# de grote vraag die dus nog moet ingevuld worden; hoe wordt het gesplit?
# splitten doet de volgende dingen:
# for region in alle genomeregions (chromosomen)
# maak nieuwe unieke naam
# call unsplittable (track, naam, region)

class TrackWriterStatUnsplittable(Statistic):
    def _init(self, outFileName, **kwArgs):
        self._outFileName = outFileName

    def _compute(self):
        f = open(self._outFileName, 'a')
        #print 'FILENAME = ' + self._outFileName

        tv = self._children[0].getResult()
        starts = tv.startsAsNumpyArray()
        ends = tv.endsAsNumpyArray()
        #print os.path.realpath(f.name)

        for segmentIndex in range(0, len(starts)):
            f.write('\t'.join([self._region.chr, str(starts[segmentIndex]), str(ends[segmentIndex])]) + '\n')
            #print '\t'.join([self._region.chr, str(starts[segmentIndex]), str(ends[segmentIndex])])

        f.close()

        return self._outFileName

    def _createChildren(self):
        self._addChild(RawDataStat(self._region, self._track, TrackFormatReq()))