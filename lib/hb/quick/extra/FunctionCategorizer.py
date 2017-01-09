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

from gold.origdata.GenomeElement import GenomeElement
from gold.origdata.GenomeElementSource import GenomeElementSource
from config.Config import DEFAULT_GENOME
from gold.track.TrackFormat import TrackFormat, TrackFormatReq
from gold.util.CommonFunctions import createOrigPath
from quick.application.UserBinSource import GlobalBinSource
from quick.extra.TrackExtractor import TrackExtractor
from gold.track.Track import PlainTrack
from gold.track.TrackView import AutonomousTrackElement
from gold.origdata.PreProcessTracksJob import PreProcessAllTracksJob

class FunctionCategorizer:
    def __init__(self, inTrackName, categorizerMethod, genome=DEFAULT_GENOME,minSegLen=0):
        self._inTrackName = inTrackName
        self._categorizerMethod = categorizerMethod
        self._genome = genome
        self._minSegLen = minSegLen
        
    def createNewTrack(self, outTrackName, username=''):
        print 'Creating segmentation...'
        self.extractToFile( createOrigPath(self._genome, outTrackName, 'generated'), outTrackName )
        print 'Preprocessing segmentation...'
        PreProcessAllTracksJob(self._genome, outTrackName, username=username).process()
        
    def extractToFile(self, fn, outTrackName):
        append = False
        for region in GlobalBinSource(self._genome):
            print 'Creating segmentation for chr: ',region.chr
            trackView = PlainTrack(self._inTrackName).getTrackView(region)
            teSource = FunctionCategorizerWrapper(trackView, self._categorizerMethod, minSegLen=self._minSegLen)
            teSource.trackFormat = TrackFormat.createInstanceFromPrefixList(['start','end','val'])
            TrackExtractor._extract(teSource, outTrackName, region, fn, append=append, globalCoords=True, addSuffix=True)
            append = True
    
# Wraps a function-TrackView (supplying TrackElements), returns valued segments as GenomeElements
class FunctionCategorizerWrapper:
    def __init__(self, functionTV, categorizer, createVoidElements=False, minSegLen=0):
        self._functionTV = functionTV
        assert(functionTV.trackFormat.getFormatName() == 'Function')
        assert(functionTV.genomeAnchor.start == 0)
        self._categorizer = categorizer
        self._genome = functionTV.genomeAnchor.genome
        self._chr = functionTV.genomeAnchor.chr
        self._createVoidElements = createVoidElements
        self._minSegLen = minSegLen
        #self._currPos = 0
        #self._currCat = None
        #self._currSegStart = 0
        
    def __iter__(self):
        return self.nextYielder()
    
    def nextYielder(self):
        prevCat = None
        prevVal = 0
        newCat = None
        currSegStart = 0
        currPos = 0

        for funcEl in self._functionTV:
            newCat = self._categorizer(funcEl.val(), funcEl.val() - prevVal)
            if newCat != prevCat:
                if (prevCat != None or self._createVoidElements) \
                    and (currPos-currSegStart >= self._minSegLen):
                    yield AutonomousTrackElement(currSegStart, currPos, prevCat)
                #else:
                #    print 'ignoring: ',currSegStart, currPos, prevCat
                currSegStart = currPos
            prevCat = newCat
            prevVal = funcEl.val()
            currPos += 1
        
        if (newCat != None or self._createVoidElements)\
           and (currPos-currSegStart >= self._minSegLen):
            yield AutonomousTrackElement(currSegStart, currPos, newCat)
            
#for i in FunctionCategorizer([GenomeElement('','chr1',val=x) for x in [1,2,3,4,5,3,1]], lambda x,y:1 if x>3 else None):
#for i in FunctionCategorizer([GenomeElement('','chr1',val=x) for x in [1,2,3,4,5,3,1,2]], lambda x,y:1 if y>0 else -1):
#for i in FunctionCategorizerWrapper([GenomeElement('','chr1',val=x) for x in [3,1,2,3,4,5,6,3,1,2]], lambda x,y:1 if y>0 else -1, True, 3):
    #print i, i.val