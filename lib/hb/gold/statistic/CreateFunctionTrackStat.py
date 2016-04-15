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
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable, StatisticSplittable
from gold.origdata.PreProcessTracksJob import PreProcessCustomTrackJob
from gold.origdata.FunctionSliceGenomeElementSource import FunctionSliceGenomeElementSource
from gold.util.CommonFunctions import isIter

class CreateFunctionTrackStat(MagicStatFactory):
    pass
    
class CreateFunctionTrackStatBase(object):
    IS_MEMOIZABLE = False
    
    def _init(self, outTrackName='', username='', valDataType='float64', **kwArgs):
        self._outTrackName = outTrackName.split('^')
        self._username = username
        self._valDataType = valDataType

class CreateFunctionTrackStatSplittable(CreateFunctionTrackStatBase, StatisticSplittable, OnlyGloballySplittable):
    def _getGESource(self, genome, trackName, region):
        return FunctionSliceGenomeElementSource(genome, trackName, region, None, self._valDataType)
    
    def _combineResults(self):
        if False in self._childResults:
            return False

        assert isIter(self._region)
        regionList = list(self._region)
        genome = regionList[0].genome
        
        job = PreProcessCustomTrackJob(genome, self._outTrackName, regionList, self._getGESource, \
                                       username=self._username, preProcess=False, finalize=True)
        job.process()
                
        return True

class CreateFunctionTrackStatUnsplittable(CreateFunctionTrackStatBase, Statistic):
    def _getGESource(self, genome, trackName, region):
        slice = self._children[0].getResult()
        return FunctionSliceGenomeElementSource(genome, trackName, region, slice, self._valDataType)
    
    def _compute(self):
        if self._kwArgs.get('minimal') == True:
            return False
        
        job = PreProcessCustomTrackJob(self._region.genome, self._outTrackName, [self._region], \
                                       self._getGESource, username=self._username, preProcess=True, finalize=False)
        job.process()

        #To reduce memory consumption
        self._children = []

        return True
        
    def _createChildren(self):
        from gold.statistic.AllStatistics import STAT_CLASS_DICT
        self._addChild( STAT_CLASS_DICT[self._kwArgs['dataStat']](self._region, self._track, self._track2 if hasattr(self,'_track2') else None, **self._kwArgs) )
