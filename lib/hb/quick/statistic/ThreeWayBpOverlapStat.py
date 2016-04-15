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
from gold.statistic.Statistic import StatisticDictSumResSplittable, MultipleRawDataStatistic
from gold.track.TrackFormat import TrackFormatReq
import numpy
from quick.util.CommonFunctions import numAsPaddedBinary

class ThreeWayBpOverlapStat(MagicStatFactory):
    '''Computes the combined overlap of different subsets of supplied tracks.
    Note that coverage by subsets is not disjunct, so that e.g. result for '01',
    denoting coverage by track2 (for two track overlap) also includes bps covered by both tracks
    '''
    pass

class ThreeWayBpOverlapStatSplittable(StatisticDictSumResSplittable):
    pass

class ThreeWayBpOverlapStatUnsplittable(MultipleRawDataStatistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        t = [child.getResult().getBinaryBpLevelArray() for child in self._children]
        binSize = len(t[0])
        res = {}
        #for i in range(3):
            #res['T%i coverage' % i] = sum(t[i])
        for comb in range(1,2**len(t)): #enumerate with binary number corresponding to all subsets
            #print 'COMB ',comb, 2**len(t)
            binary = numAsPaddedBinary(comb,len(t))
            trackIndicator = numpy.empty(binSize,dtype='bool')
            trackIndicator[:] = True
            for tIndex, doInclude in enumerate(binary):
                if doInclude == '1':
                    trackIndicator &= t[tIndex]
            res[binary] = trackIndicator.sum()
        return res

    def _getTrackFormatReq(self):
        return TrackFormatReq(dense=False)
