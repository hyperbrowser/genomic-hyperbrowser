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

from gold.result.GraphicsPresenter import GraphicsPresenter, LocalResultsGraphicsData
from quick.util.CommonFunctions import ensurePathExists
import os
import numpy
#from proto.RSetup import r

class LinePlotPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('line','Line plot')
    dataPointLimits = (2,1e6)

    def _getRawData(self, resDictKey, avoidNAs=True):
        rawDict = self._results.getGlobalResult().get(resDictKey)
        xList = rawDict.keys()
        xList = sorted(x for x in xList if not (avoidNAs and numpy.isnan(rawDict[x])))
        yList = [rawDict[x] for x in xList]
        return xList, yList, rawDict.getXLabel(), rawDict.getYLabel()

    def _writeRawData(self, resDictKey, fn):
        ensurePathExists(fn)
        xList, yList, xLabel, yLabel = self._getRawData(resDictKey, False)
        outF = open(fn,'w')
        outF.write( xLabel +': ' + ','.join([ str(x) for x in xList]) + os.linesep )
        outF.write( yLabel + ': ' + ','.join([ str(x) for x in yList]) + os.linesep )

    def _customRExecution(self, resDictKey, xlab, main):
        from proto.RSetup import r, robjects
        
        xList, yList, xLabel, yLabel = self._getRawData(resDictKey)
        xVec = robjects.FloatVector(xList)
        yVec = robjects.FloatVector(yList)

        rCode = 'plotFunc <- function(xVec, yVec, xlab, ylab, main) {plot(xVec, yVec, type="l", xlab=xlab, ylab=ylab, main=main)}'
        
        #print (xs, ys, xlab, main)
        #print 'rawData: ',self._getRawData(resDictKey)
        r(rCode)(xVec, yVec, xLabel, yLabel, main)
        
        self._plotResultObject = r('dataFunc <- function(xVec, yVec) {list("x"=xVec, "y"=yVec)}')(xVec, yVec)
