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
from numpy import isnan
#from proto.RSetup import r
 
class DensityPresenter(LocalResultsGraphicsData, GraphicsPresenter):
    name = ('density','Density plot')
    dataPointLimits = (2,None)

    #def _getRawData(self, resDictKey, avoidNAs=True):
    #    return [x for x in self._results.getAllValuesForResDictKey(resDictKey) if not (avoidNAs and isnan(x))]
        ##if self._results.getGlobalResult() is not None:
        ##    return self._results.getGlobalResult().get(resDictKey)
        ##else:
        ##    return None

    def _customRExecution(self, resDictKey, xlab, main):
        fromTo = ',from=0,to=1' if resDictKey == 'p-value' else ''
        rCode = 'plotFunc <- function(ourList, xlab, main) {vec <- unlist(ourList); plot(density(vec'+fromTo+'), xlab=xlab, main=main)}'
        #print (self._getRawData(resDictKey), xlab, main)
        rawData = [float(x) for x in self._getRawData(resDictKey)]
        from proto.RSetup import r
        r(rCode)(rawData, xlab, main)
        
        
class DensityGlobalListPresenter(GlobalResultGraphicsData, DensityPresenter):
    dataPointLimits = (2,None)
    #def _getRawData(self, resDictKey, avoidNAs=True):
    #    if self._results.getGlobalResult() is not None:
    #        return self._results.getGlobalResult().get(resDictKey)
    #    else:
    #        return None
    #
    #def _getDataPointCount(self,resDictKey):
    #    if self._results.getGlobalResult() is not None:
    #        return len(self._results.getGlobalResult().get(resDictKey))
    #    else:
    #        return 0
    #
