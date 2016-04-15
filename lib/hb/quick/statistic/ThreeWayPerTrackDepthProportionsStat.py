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
from quick.util.CommonFunctions import numAsPaddedBinary
from collections import OrderedDict
import numpy
from quick.statistic.MultitrackBpOverlapStat import MultitrackBpOverlapStat

class ThreeWayPerTrackDepthProportionsStat(MagicStatFactory):
    pass
            
class ThreeWayPerTrackDepthProportionsStatUnsplittable(Statistic):        
    @staticmethod
    def _getPaddedBinaryRange(numTracks):
        '''Returns a list of all binary numbers, in the form of zero-padded strings, from 1 to 2^numTracks (exclusive)
        i.e. _getPaddedBinaryRange(2) will return ['00','01','10','11']
        '''
        paddedBinaryNumbers = []
        for comb in range(1,2**numTracks):
            paddedBinaryNumbers.append( numAsPaddedBinary(comb,numTracks) )
        return paddedBinaryNumbers
        
    def _compute(self):
        t = self._children[0].getResult()
        numTracks = len(t.keys()[0])
#         allBinaries = self._getPaddedBinaryRange(numTracks)
        proportions = [] #contains triplets of resultDictKey, list of numerator binaries, list of denominator binaries
        for focusTrackIndex in range(numTracks):
            for inclusiveDepth in range(1,numTracks+1):
                #numerator = ["0"]*numTracks
                #numerator[focusTrackIndex]="1"
                #numerator = ''.join(numerator)
                
                #denominator = [binary for binary in self._getPaddedBinaryRange(numTracks)
                #               if binary[focusTrackIndex]=="1" and binary.count("1")==inclusiveDepth]
                numerator = [binary for binary in self._getPaddedBinaryRange(numTracks)
                               if binary[focusTrackIndex]=="1" and binary.count("1")==inclusiveDepth]
                denominator = [binary for binary in self._getPaddedBinaryRange(numTracks)
                               if binary[focusTrackIndex]=="1"]
                
                key = 'T' + str(focusTrackIndex) + ' covered by ' + str(inclusiveDepth-1) + " other tracks"                
                proportions.append( [key, numerator, denominator ] )
        
        
        res = OrderedDict()
        for prop in proportions:
            key = prop[0]
            num, denom = [sum(t[n] for n in prop[i]) for i in [1,2] ]
            res[key] = float(num)/denom if denom!=0 else numpy.nan
            
        return res
    
    def _createChildren(self):
#         self._addChild( ThreeWayBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )        
        self._addChild( MultitrackBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )        
        
