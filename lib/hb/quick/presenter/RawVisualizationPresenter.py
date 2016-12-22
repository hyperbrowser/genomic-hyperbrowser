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

from gold.result.GraphicsPresenter import GraphicsPresenter#, LocalResultsGraphicsData, GlobalResultGraphicsData
#from proto.RSetup import r
#import os

#class VisualizationPresenter(LocalResultsGraphicsData, GraphicsPresenter):
class RawVisualizationPresenter(GraphicsPresenter):
    def _getDataPointCount(self, resDictKey, avoidNAs=True):
        #In this case, we consider number of rows as data points, to be set min and max values for..
        if self._results.getGlobalResult() is not None and self._results.getGlobalResult().get(resDictKey) is not None:
            return len(self._results.getGlobalResult().get(resDictKey).getAllTrackViews()) #is supposed to be a list of trackviews..
        else:
            return 0

    def _getRawData(self, resDictKey, avoidNAs=True):
        assert resDictKey=='Result' #temporarily..
        globRes = self._results.getGlobalResult()
        assert len(globRes)==1
        visRes = self._results.getGlobalResult().values()[0]
        return visRes.getAllTrackViews()

    def getReference(self, resDictKey, fullImage=False):
        return GraphicsPresenter.getReference(self, resDictKey, imageLink=True, fullImage=fullImage)

    name = ('RawVisualizationPresenter', 'Plot: Raw data, with each bin on a separate line')
    dataPointLimits = (1,200)
    maxRawDataPoints = None#30000
            
    def _customRExecution(self, resDictKey, xlab, main):
        #rCode = 'ourHist <- function(ourList, xlab, main, numBins) {vec <- unlist(ourList); hist(vec, col="blue", breaks=numBins, xlab=xlab, main=main)}'
        
        rCode = ''' par(mar=c(4.2, 0.2, 0.2, 14.2))\n
        plot.new()\n
            plot.window(xlim=c(0,%i),ylim=c(0,1000))\n
            axis(1)\n
            axis(4, at=((1:%i)*20)-14, lab=c(%s), las=1)\n
            %s
        '''
        
        yFloor = 1
        rectTemplate = 'rect(%f,%i,%f,%i, col="%s", border="%s")\n'
        rectVals = []
        rawData = self._getRawData(resDictKey)
        yLabels = []
        maxVal = max([tv._bpSize() for tv in rawData])
        halfMax = maxVal/2
        for tv in rawData:
            #print tv.genomeAnchor,
            # print tv.genomeAnchor.chr
            yLabels.append('"'+tv.genomeAnchor.chr+': %s"'% ':'.join(str(tv.genomeAnchor).split()[0].split(':')[1:]))
            startArr, endArr = tv.startsAsNumpyArray(),tv.endsAsNumpyArray()
            if tv.normalizeRows:
                normalizer = 1000.0/tv._bpSize() if len(endArr)>0 else 0
                maxVal = 1000
                rectVals.append(rectTemplate % (0, yFloor+5, 1000, yFloor+5, 'lightgray', 'lightgray') )
                
                rectVals += [rectTemplate % (start*normalizer, yFloor, end*normalizer, yFloor+10, 'red', 'red') for start, end in zip(startArr, endArr)]
            else:
                extra1=extra2 = 0
                if tv.centerRows:
                    halfBin = tv._bpSize()/2
                    extra1 = halfMax-halfBin
                    extra2 = halfMax+halfBin
                    
                rectVals.append(rectTemplate % (0+extra1, yFloor+5, extra2 if tv.centerRows else tv._bpSize()  , yFloor+5, 'lightgray', 'lightgray') )
                rectVals += [rectTemplate % (start+extra1, yFloor, end+extra1, yFloor+10, 'red', 'red') for start, end in zip(startArr, endArr)]
            yFloor+=20
        
        from proto.RSetup import r
        #numericX = (type(xList[0]) in [int,float])
        if len(rectTemplate)>0:
            rScript = rCode % (maxVal,len(yLabels), ','.join(yLabels), '\n'.join(rectVals))
            
            #print rScript[:2000]
            self._plotResultObject = r(rScript)
        
        #)(xList, list(scaledYLists[0]), list(scaledYLists[1]), list(scaledYLists[2]), numericX)
        
        
        
        
        
        
        
