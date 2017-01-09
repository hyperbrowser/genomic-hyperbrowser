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

#Quick, due to quick code within _getRawData.
#Also, having two objects from one of these classes each, will mean that most computations inside _getRawData are done equally two times (no caching between these two classes) ...
#Maybe this means that functionality really belongs in results, although it is a bit specialized..

from gold.result.ScatterPresenter import ScatterPresenter
#from config.Config import brk

#from proto.RSetup import r
import numpy

class BinHistPresenter(ScatterPresenter):
    name = ('xHist','Histogram of x-values')
    X_LAB = 'Binning based on track1-values'
    Y_LAB = 'Number of track1-values falling in each histogram-bin'
    dataPointLimits = (2,1e8) 

    def __init__(self, results, baseDir, header, binSize=1):
        self._binSize = binSize
        self._rawData = None
        ScatterPresenter.__init__(self, results, baseDir, header)

    def _getRawData(self, resDictKey,avoidNAs=True):
        if self._rawData is None:            
            pairs = [x for x in self._results.getAllValuesForResDictKey(resDictKey) if x is not None and not any(numpy.isnan(val) for val in x)]
            minX = min(x[0] for x in pairs)
            #maxX = max(x[0] for x in pairs)
            binnedYs = {}
            for x,y in pairs:
                #brk()
                binNum = int( (x-minX) / self._binSize )
                binX = minX + self._binSize*(binNum+0.5)
                if not binX in binnedYs:
                    binnedYs[binX] = [0,0]
                binnedYs[binX][0] += 1
                binnedYs[binX][1] += y
                
            self._rawData = self._rawDataFromBinning(binnedYs)
            
        return self._rawData

    def _rawDataFromBinning(self, binnedYs):
        sortedBins = sorted(binnedYs.keys())
        return sortedBins, [ binnedYs[bin][0] for bin in sortedBins ]

    def _customRExecution(self, resDictKey, xlab, main):
        rCode = 'plotFunc <- function(xs, ys, xlab,ylab, main) {xVec <- unlist(xs); yVec <- unlist(ys); plot(xVec, yVec, xlab=xlab,ylab=ylab, main=main, type="l")}'
        xs, ys = self._getRawData(resDictKey)
        from proto.RSetup import r
        r(rCode)(xs, ys, self.X_LAB, self.Y_LAB, main)
        
class MeanLinePresenter(BinHistPresenter):
    name = ('meanLine','Mean y, binned on x')
    dataPointLimits = (2,1e8) 
    X_LAB = 'Binning based on track1-values'
    Y_LAB = 'Mean track2-value for each analysis region falling in given (track1-based) histogram-bin'

    def _rawDataFromBinning(self, binnedYs):
        sortedBins = sorted(binnedYs.keys())
        return sortedBins, [ (1.0*binnedYs[bin][1]/binnedYs[bin][0]) for bin in sortedBins ]
