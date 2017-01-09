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
from quick.statistic.BinSizeStat import BinSizeStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import InvalidFormatError
from gold.track.TrackView import TrackView
from gold.util.CommonFunctions import getStringFromStrand  
import numpy as np

class SplitToCorrespondingSubBinsBasedOnBreakpointsStat(MagicStatFactory):
    pass

#class SplitToCorrespondingSubBinsBasedOnBreakpointsStatSplittable(StatisticSumResSplittable):
#   pass
            
class SplitToCorrespondingSubBinsBasedOnBreakpointsStatUnsplittable(Statistic):    
    def _compute(self):
        
        binSize = self._children[0].getResult()
        tv = self._children[1].getResult()
        starts = list(tv.startsAsNumpyArray())
        ends = starts[:]
        vals = strandType = strandList = None
        if len(starts)>0:
            if starts[0]>0:
                starts.insert(0, 0)
            else:
                del ends[0]
                
            if len(ends)==0 or ends[-1]<binSize-1:
                ends.append(binSize-1)
            else:
                del starts[-1]
            
            strands = tv.strandsAsNumpyArray()
            
            if strands != None:
                strands = set(strands)
                if len(strands)>1:
                    raise InvalidFormatError('All strands within a bin must be of same sort: error at %s' % (tv.genomeAnchor))
                strandType = strands.pop()
                strandList = [strandType]*len(starts)
            
            vals = range(len(starts)-1, -1,-1) if strandType == 0 else range(len(starts))
            
            starts = np.array(starts) + tv.genomeAnchor.start
            ends = np.array(ends) + tv.genomeAnchor.start
        
        
        strTemplate = self._region.chr + '\t%s\t%s\t%s\t'+getStringFromStrand(strandType)
        return '\n'.join([strTemplate % (str(starts[i]), str(ends[i]),  str(vals[i])) for i in xrange(len(starts))])
    
        return TrackView(genomeAnchor=tv.genomeAnchor, startList=starts, endList=ends, valList=vals, \
                         strandList=strandList, idList=None, edgesList=None, weightsList=None, borderHandling=tv.borderHandling, allowOverlaps=tv.allowOverlaps)
        
            
    def _createChildren(self):
        self._addChild( BinSizeStat(self._region, self._track) )
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(interval=False, dense=False)) )
        