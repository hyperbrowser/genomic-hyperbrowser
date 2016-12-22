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

class LinePlotResultType(dict):
    def setXLabel(self, xLabel):
        self._xLabel = xLabel
        
    def setYLabel(self, yLabel):
        self._yLabel = yLabel
        
    def getXLabel(self):
        return self._xLabel if hasattr(self, '_xLabel') else 'X-values'
        
    def getYLabel(self):
        return self._yLabel if hasattr(self, '_yLabel') else 'Y-values'

class GlobalVisualizationResultType:
    def __init__(self, localResults):
        #self._localResults = localResults
        lists = zip(*localResults)
        regs = lists[0]
        if len(set([reg.chr for reg in regs])) == 1:
            #only single chromosome
            self._xList = [reg.start for reg in regs]
        else:
            self._xList = ['%s-%i'%(reg.chr,reg.start) for reg in regs]
        
        self._yLists = lists[1:]
        
    def getXlist(self):
        return self._xList
    
    def getYlists(self):
        return self._yLists
    
class RawVisualizationResultType:
    def __init__(self, localTrackViews):
        self._localTrackViews = localTrackViews
        
    def getAllTrackViews(self):
        return self._localTrackViews
    
#class GlobalVisualizationResultType(dict):
#    def __init__(self, localResults):
#        #self._localResults = localResults
#        lists = zip(*localResults)
#        regs = lists[0]
#        assert len(set([x.chr for x in regs])) == 1, 'for now, only support single chromosome'
#        self['xList'] = [x.start for reg in regs]
#        
#        self['yLists'] = lists[1:]
#        
#    def getXlist(self):
#        return self['xList']
#    
#    def getYlists(self):
#        return self['yLists']

class FunctionDefResultType(object):
    #@takes(str,list)
    def __init__(self, functionText, testTexts):
        self.functionText = functionText
        self.testTexts = testTexts
    
    def __add__(self, other):
        assert self.functionText == other.functionText
        #self.testTexts.append(other.testTexts)
        #return self
        return FunctionDefResultType(self.functionText, self.testTexts+other.testTexts)
    
    def __str__(self):
        text = self.functionText + '\n' + '\n'.join(self.testTexts)
        return text
        #return text.replace('\n','<br>')
        #from proto.hyperbrowser.StaticFile import
