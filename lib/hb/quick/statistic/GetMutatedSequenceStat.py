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
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq

class GetMutatedSequenceStat(MagicStatFactory):
    pass

#class GetMutatedSequenceStatSplittable(StatisticSumResSplittable):
#    pass
    
class GetMutatedSequenceStatUnsplittable(Statistic):    
    
    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        tv1 = self._children[0].getResult()
        tv2 = self._children[1].getResult()
        
        fastaSequence = list(tv1.valsAsNumpyArray())
        mutationStarts, mutationValues = tv2.startsAsNumpyArray(), list(tv2.valsAsNumpyArray())
        if len(mutationValues)>0 and mutationValues[0].find('>')>=0:
            mutationValues = [v[-1] for v in mutationValues]
        for index, mutationPos in enumerate(mutationStarts):
            fastaSequence[mutationPos] = mutationValues[index]
            #fastaSequence.insert(mutationPos+1, '#'+mutationValues[index])
        
        return ''.join(fastaSequence)
    
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(dense=True, val='char')) )
        self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(val='category')) )
        
        
        
        