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

import ast

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
import numpy as np

class PwmScoreArrayStat(MagicStatFactory):
    pass

#class PwmScoreArrayStatSplittable(StatisticSumResSplittable):
#    pass
            
class PwmScoreArrayStatUnsplittable(Statistic):
    def _init(self, pfmFileName='', complement='False', **kwArgs):
        assert pfmFileName != ''
        self._pfmFileName = pfmFileName.replace('^','/')
        
        assert complement in ['True', 'False']
        self._complement = ast.literal_eval(complement)

    def _compute(self):
        from Bio.Alphabet import IUPAC
        from Bio.Seq import Seq
        from Bio import Motif
        
        sequence = self._sequenceStat.getResult().valsAsNumpyArray()
        bioSeq = Seq(sequence.tostring(), alphabet=IUPAC.unambiguous_dna)

        thisPwm = Motif.read(open(self._pfmFileName), "jaspar-pfm")
        if self._complement:
            thisPwm = thisPwm.reverse_complement()
            
        try:
            pwmScoreArray = thisPwm.scanPWM(bioSeq)
        except MemoryError, e: #when sequence is shorter than pwm
            return
        
        pwmScoreArray = np.append( pwmScoreArray, np.zeros(len(thisPwm)-1) + np.nan )
        return pwmScoreArray
    
    def _createChildren(self):
        self._sequenceStat = self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(val='char', dense=True, interval=False)) )
