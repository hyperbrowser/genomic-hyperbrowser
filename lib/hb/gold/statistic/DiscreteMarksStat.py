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
from gold.statistic.MinAndMaxStat import MinAndMaxStat
from gold.statistic.Statistic import Statistic


class DiscreteMarksStat(MagicStatFactory):
    pass

#class DiscreteMarksStatSplittable(StatisticSumResSplittable):
#    IS_MEMOIZABLE = False
            
class DiscreteMarksStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False

    def __init__(self, region, track, track2=None, numDiscreteVals=None, marksStat='MarksListStat', printIntervals=False, **kwArgs):
        self._numDiscreteVals = int(numDiscreteVals)
        self._marksStat = marksStat
        assert numDiscreteVals is not None
        self._printIntervals = printIntervals
        Statistic.__init__(self, region, track, track2, numDiscreteVals=numDiscreteVals, marksStat=marksStat, **kwArgs)

    def _compute(self):
        vals = self._children[0].getResult()
        #print 'DEBUG INFO - nr of marks from stat %s is: %s' % (self._marksStat, len(vals))
        minVal, maxVal = [self._children[1].getResult()[x] for x in ['min','max']]
        if maxVal != minVal:
            step = 1.0*(maxVal-minVal) / self._numDiscreteVals
            #             from gold.statistic.BpIntensityStat import BpIntensityStatUnsplittable
            #if BpIntensityStatUnsplittable.VERBOSE_INTENSITY_CREATION or IS_EXPERIMENTAL_INSTALLATION:
            #    print '<br>'
            #    print 'Discretizing with marksStat: ', self._marksStat, ' in region: ', self._region
            #    print '<br>In discretization, using steps: ',\
            #          ','.join([str(minVal+i*step) for i in range(self._numDiscreteVals)] )
            #    print '<br>'
            if self._printIntervals:
                from proto.hyperbrowser.HtmlCore import HtmlCore
                steps = [minVal+i*step for i in range(self._numDiscreteVals)]
                row = [str(self._region)] + ['%.1e:%.1e'%(steps[i-1],steps[i]) for i in range(1, len(steps))] + ['%.1e-'%steps[-1]]
                print HtmlCore().tableHeader(row, firstRow=False)

            
        else:
            step = 1.0 / self._numDiscreteVals
            
        res = ((vals-minVal)/step).astype('int32')
        res[ res==self._numDiscreteVals ] = self._numDiscreteVals-1 #because our max is an inclusive max of the allowed interval..
        return res
    
    def _createChildren(self):
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._addChild( STAT_CLASS_DICT[self._marksStat](self._region, self._track, (self._track2 if hasattr(self,'_track2') else None)) )
        self._addChild( MinAndMaxStat(self._region, self._track) )
