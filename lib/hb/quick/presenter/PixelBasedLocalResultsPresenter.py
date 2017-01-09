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

from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData, GlobalResultGraphicsData
from gold.util.CustomExceptions import SilentError
from math import log
import os

class PixelBasedLocalResultsPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('pixel', 'Plot: pixel-colored local results')
    dataPointLimits = (2,None)
    maxRawDataPoints = 5e5
    
    #def _checkCorrectData(self, resDictKey):
    #    try:
    #        data = self._getRawData(resDictKey)
    #        if len(data) > 0:            
    #            data[0] + 1
    #    except:
    #        return False
    #    return True
        
    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        rCode = '''
        plot(2,2)
        '''
        
        rawData = self._getRawData(resDictKey) #A python list of values..
        #rawData = [float(x) for x in self._getRawData(resDictKey)]        
        self._plotResultObject = r(rCode) #()

#class HistogramGlobalListPresenter(GlobalResultGraphicsData, HistogramPresenter):
#    dataPointLimits = (2, None)
#
#class LogHistogramGlobalListPresenter(HistogramGlobalListPresenter):
#    name = ('hist_log', 'Plot: histogram of log-transposed values')
#    
#    def _getRawData(self, resDictKey, avoidNAs=True):
#        return [log(x) for x in HistogramGlobalListPresenter._getRawData(self, resDictKey) if x>0]
#        
#    def _customRExecution(self, resDictKey, xlab, main):
#        HistogramGlobalListPresenter._customRExecution(self, resDictKey, xlab + ' (log-transposed)', main)
