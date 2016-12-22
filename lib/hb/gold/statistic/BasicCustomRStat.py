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
from gold.track.TrackFormat import TrackFormatReq
from numpy import nan
#from proto.RSetup import r

class BasicCustomRStat(MagicStatFactory):
    pass

#class BasicCustomRStatSplittable(StatisticSumResSplittable):
#    pass

class BasicCustomRStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def _init(self, scriptFn='', randomSeed=None, **kwArgs):
        self._trackFormat1 = TrackFormatReq()
        self._trackFormat2 = TrackFormatReq()
        self._codeLines = []
        if scriptFn != '':
            self._parseScriptFile(scriptFn.decode('hex_codec'))
    
        from gold.util.RandomUtil import getManualSeed, setManualSeed
        if randomSeed is not None and randomSeed != 'Random' and getManualSeed() is None:
            setManualSeed(int(randomSeed))
        
    def _parseScriptFile(self, scriptFn):        
        script = open(scriptFn)
        for line in script:
            if line.lower().startswith('#format1:'):
                format = line.replace('#format1:','').strip()
                self._trackFormat1 = TrackFormatReq( name=format )
            elif line.lower().startswith('#format2:'):
                format = line.replace('#format2:','').strip()
                self._trackFormat2 = TrackFormatReq( name=format )
            elif line[0] == '#':
                pass
            else:
                self._codeLines.append( line.strip() )
    
    def _compute(self):
        #try:
        track = [None, None]
        for i in [0,1]:
            tv = self._children[i].getResult()
            track[i] = []
            for index, el in enumerate(tv):
                if el.start() == el.end() == None:
                    track[i] += [index, index+1, float(el.val())]
                else:                    
                    track[i] += [int(el.start()), int(el.end()), int(float(el.val())) if el.val() is not None else nan]
        
        #print "track 0 before unlist: " %, track[0]
        #print "track 1 before unlist: " % track[1] 
        header = ['rCompute <- function(track1, track2) {',
                  #'track1[unlist(sapply(track1,is.null))] <- NA',
                  #'track2[unlist(sapply(track2,is.null))] <- NA',
                  #'track1 <- unlist(track1)',
                  #'track2 <- unlist(track2)',
                  'dim(track1) <- c(3,' + str(len(track[0])/3) + ')',
                  'dim(track2) <- c(3,' + str(len(track[1])/3) + ')',
                  'result <- 0']
        footer = ['return(result)','}']
        allLines = header + self._codeLines + footer 
        
        from proto.RSetup import r, robjects
        
        track[0] = robjects.FloatVector(track[0])
        #print "track 0 after unlist: ", track[0]
        track[1] = robjects.FloatVector(track[1])    
        #print "track 1 after unlist: ", track[1]

        return r('\n'.join(allLines))(track[0], track[1])        
        #=======================================================================
        # except Exception, e:
        #    print 'Exception in the custom R code:'
        #    print e.__class__.__name__ + ':', e
        #    raise e
        #=======================================================================
        
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, self._trackFormat1) )
        self._addChild( RawDataStat(self._region, self._track2, self._trackFormat2) )
