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
from gold.statistic.PointCountPerSegStat import PointCountPerSegStat
#from proto.RSetup import r
from quick.util.CommonFunctions import silenceRWarnings
from gold.statistic.MarksListStat import MarksListStat
from collections import OrderedDict

class PointFreqInSegsVsSegMarksStat(MagicStatFactory):
    pass

#class PointFreqInSegsVsSegMarksStatSplittable(StatisticSumResSplittable):
#    pass
            
class PointFreqInSegsVsSegMarksStatUnsplittable(Statistic):
    '''Assumes segments of equal length or segment length considered unimportant.
       Currently also assumes that no segments crosses bin borders.'''

    MIN_NUM_SEGS_FOR_TEST = 10

    def __init__(self, region, track, track2, markType='number', **kwArgs):
        self._markType = markType
        #r('sink(file("/dev/null", open="wt"), type="message")')
        silenceRWarnings()
        
        Statistic.__init__(self, region, track, track2, markType=markType, **kwArgs)
        
    def _compute(self):
        numPoints = self._numPointsPerSeg.getResult()
        
        #marks = self._markedSegs.getResult().valsAsNumpyArray()
        marks = self._markPerSeg.getResult()
        
        assert len(numPoints) == len(marks)
        
        if len(marks)==0 or numPoints.sum()==0:
            return None
        
        if len(marks) < self.MIN_NUM_SEGS_FOR_TEST:
            return None
        
        rVecCor = 'ourCor <- function(ourList1, ourList2) '+\
                  '{ vec1 <- unlist(ourList1); vec2 <- unlist(ourList2); '+\
                  'res <- cor.test(vec1,vec2,method="kendall");'+\
                  "return(c(res[['p.value']], res[['estimate']][['tau']]))}"
        # wilcox.test... (5 paa hver)
        #cor.test: 10 tilsammen..
        #return r(rVecCor)(list(numPoints), list(marks.astype('i')))
        if self._markType == 'number':
            compatibleMarks = [float(x) for x in marks]
        elif self._markType == 'tc':
            compatibleMarks = [int(x) for x in marks]
        compatibleNumPoints = [int(x) for x in numPoints]

        #from proto.RSetup import rpy1
        #res = rpy1(rVecCor)(compatibleNumPoints, compatibleMarks )
        from proto.RSetup import r
        pval, tau = r(rVecCor)(compatibleNumPoints, compatibleMarks )
        #print float(res['p.value'])
        
        #print type(res)
        #print 'RES: ', dict(res)
        #print 'RES: ', res.keys()
        #print repr(res['estimate'])
        #tau = res['estimate']['tau']
        #pval = float(res['p.value'])
                
        return OrderedDict([ ('P-value', pval), ('Test statistic: ObservedTau', tau), \
                            ('NumberOfSegments', len(marks)), ('AverageNumberOfPointsInSegments', 1.0*numPoints.sum()/len(marks)) ])
    
    def _createChildren(self):
        self._numPointsPerSeg = self._addChild( PointCountPerSegStat(self._region, self._track, self._track2))
        self._markPerSeg = self._addChild( MarksListStat(self._region, self._track2, markType=self._markType, enforcePoints=False))
        #self._markedSegs = self._addChild( RawDataStat(self._region, self._track2, TrackFormatReq(val=self._markType)) )

        
