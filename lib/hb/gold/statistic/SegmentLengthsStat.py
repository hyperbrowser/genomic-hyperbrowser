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
from gold.statistic.Statistic import Statistic, StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from collections import OrderedDict

class SegmentLengthsStat(MagicStatFactory):
    pass

class SegmentLengthsStatSplittable(StatisticConcatDictOfNumpyArrayResSplittable, OnlyGloballySplittable):
    IS_MEMOIZABLE = False

class SegmentLengthsStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def _init(self, withOverlaps='no', **kwArgs):
        assert( withOverlaps in ['no','yes'] )
        self._withOverlaps = withOverlaps

    def _compute(self):
        tv = self._children[0].getResult()
        nameArray = tv.extrasAsNumpyArray('name') if tv.hasExtra('name') else \
                    tv.idsAsNumpyArray()
        
        return OrderedDict([('Result', tv.endsAsNumpyArray()-tv.startsAsNumpyArray())] + \
                           ([('Names' if tv.hasExtra('name') else 'Ids', nameArray)] if nameArray is not None else []))
        #return [(seg.end()-seg.start()) for seg in self._children[0].getResult()]
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=True, \
                                                                              allowOverlaps = (self._withOverlaps == 'yes') ) ) )
