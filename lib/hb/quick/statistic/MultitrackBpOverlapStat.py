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
'''
Created on Jun 24, 2015

@author: boris
'''


from collections import OrderedDict
from gold.statistic.MultitrackRawOverlapStat import MultitrackRawOverlapStat
from quick.util.CommonFunctions import numAsPaddedBinary
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic,\
    StatisticDictSumResSplittable
from gold.util.CommonConstants import MULTIPLE_EXTRA_TRACKS_SEPARATOR


class MultitrackBpOverlapStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass

class MultitrackBpOverlapStatSplittable(StatisticDictSumResSplittable):
    pass
            
class MultitrackBpOverlapStatUnsplittable(Statistic):    
    def _compute(self):
#         import sys
#         sys.path.append(r'/software/VERSIONS/python2-packages-2.7_2/lib/python2.7/site-packages/pysrc')
#         import pydevd
#         pydevd.settrace('localhost', stderrToServer=True, stdoutToServer=True)
        assert 'extraTracks' in self._kwArgs, self._kwArgs
        assert self._track2 is not None, 'self._track2 missing'
        
        extraTracksArg = self._kwArgs['extraTracks']
        assert isinstance(extraTracksArg, (list, str)), extraTracksArg
        if isinstance(extraTracksArg, str):
            extraTracksArg = extraTracksArg.split(MULTIPLE_EXTRA_TRACKS_SEPARATOR)
        numTracks = 2 + len(extraTracksArg)
        
        resDict = OrderedDict()
        childeRes = self._children[0].getResult()
        
        combBinList = [numAsPaddedBinary(comb, numTracks) for comb in xrange(1, 2**numTracks)] #list of all subset combinations, we want them sorted by number of elements.
        combBinList.sort(key=lambda x: x.count('1'), reverse=True) #sort by number of elements in subset of tracks descending, the order is important for the summing done later
        intermediateResults = {} 
        for combBin in combBinList:
            level = combBin.count('1')
            if level not in intermediateResults:
                intermediateResults[level] = {}
            accumulatedOverlap = 0
            for superSetLevel in intermediateResults:
                if superSetLevel > level:
                    for superSetComb in intermediateResults[superSetLevel]:
                        if long(combBin, 2) == (long(superSetComb, 2) & long(combBin, 2)):
                            accumulatedOverlap += childeRes[long(superSetComb, 2)]
            intermediateResults[level][combBin] = childeRes[long(combBin, 2)] + accumulatedOverlap
        
#         for level in intermediateResults:
#             for combBin in intermediateResults[level]:
        for combBin in combBinList[::-1]:
            resDict[combBin[::-1]] = intermediateResults[combBin.count('1')][combBin]
        
#         for key, val in childeRes.iteritems():
#             resDict[numAsPaddedBinary(key, numTracks)] = val
        return resDict
    
    def _createChildren(self):
        self._addChild(MultitrackRawOverlapStat(self._region, self._track, self._track2, **self._kwArgs))
