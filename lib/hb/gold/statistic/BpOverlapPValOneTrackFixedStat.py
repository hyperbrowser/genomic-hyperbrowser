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
from gold.statistic.Statistic import Statistic
from gold.statistic.RawSegsOverlapStat import RawSegsOverlapStat
from gold.util.CustomExceptions import IncompatibleAssumptionsError
from quick.statistic.CommonStatisticalTests import BinomialTools
from collections import OrderedDict

class BpOverlapPValOneTrackFixedStat(MagicStatFactory):
    pass

#class BpOverlapPValStatSplittable(StatisticSumResSplittable):
#    pass
            
class BpOverlapPValOneTrackFixedStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, tail='more', **kwArgs):
        assert( tail in ['less','more','different'])
        self._tail = tail
        Statistic.__init__(self, region, track, track2, tail=tail, **kwArgs)

    def _checkAssumptions(self, assumptions):
        if not assumptions == 'Tr1IndependentBps':
            raise IncompatibleAssumptionsError
    
    def _compute(self):
        
        neither,only1,only2,both = [ self._children[0].getResult()[key] for key in ['Neither','Only1','Only2','Both'] ]
        all = neither+only1+only2+both
        size = only2+both
        prob = 1.0*(only1+both)/all
        x = both

        if both == 0 and (only1 == 0 or only2 == 0):
            pval = None
        else:
            pval = BinomialTools._computeBinomialTail(x, size, prob, self._tail)
        return OrderedDict([('P-value', pval), ('Test statistic: ObsBpOverlap', x), ('E(Test statistic): ExpBpOverlap', prob*size), \
                            ('DiffFromMean', x-prob*size), ('BpsInTrack2Segments', size), ('NumBpInBin', all), \
                            ('track1Coverage', (1.0*(only1+both)/all)), ('track2Coverage', (1.0*(only2+both)/all))])
    
    def _createChildren(self):
        self._addChild( RawSegsOverlapStat(self._region, self._track, self._track2) )
