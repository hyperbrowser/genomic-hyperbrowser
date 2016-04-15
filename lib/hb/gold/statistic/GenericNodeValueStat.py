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
from gold.statistic.Statistic import Statistic, StatisticConcatDictResSplittable
from gold.statistic.RawDataStat import RawDataStat
#from gold.statistic.SumOverCoveredBpsStat import SumOverCoveredBpsStat
#from gold.track.TrackFormat import TrackFormatReq
#from gold.track.TrackView import TrackView
from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackFormat import TrackFormatReq

#import numpy as np

class GenericNodeValueStat(MagicStatFactory):
    pass

class GenericNodeValueStatSplittable(StatisticConcatDictResSplittable):
    pass
            
class GenericNodeValueStatUnsplittable(Statistic):
    def _init(self, rawStatistic=None, **kwArgs):
        self._rawStatistic = rawStatistic
    
    def _compute(self):
        tv = self._children[0].getResult()
        ga = tv.genomeAnchor
        nodeBins = [GenomeRegion(self._region.genome, ga.chr, ga.start+x.start(), ga.start+x.end()) for x in tv]
        nodeBinIds = [x.id() for x in tv]
        nodeBinResults = [self._rawStatistic(nodeBin, self._track2).getResult() for nodeBin in nodeBins]
        return dict(zip(nodeBinIds, nodeBinResults))
            
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(linked=True)) )
        

