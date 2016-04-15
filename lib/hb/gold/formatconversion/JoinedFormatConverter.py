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

from gold.formatconversion.FormatConverter import FormatConverter
#from gold.formatconversion.SegmentToPointFormatConverter import SegmentToStartPointFormatConverter, \
#    SegmentToMidPointFormatConverter, SegmentToEndPointFormatConverter

class JoinedFormatConverter(FormatConverter):
    _formatConverterClsList=[]
    
    def __init__(self, sourceFormat=None, reqFormat=None):
        FormatConverter.__init__(self, sourceFormat, reqFormat)
        self._formatConverters = []
        for formatConverterCls in self._formatConverterClsList:
            formatConverter = object.__new__(formatConverterCls, sourceFormat, reqFormat)
            formatConverter.__init__(sourceFormat, reqFormat)
            self._formatConverters.append(formatConverter)
        
    def convert(self, tv):
        for formatConverter in self._formatConverters:
            tv = formatConverter.convert(tv)
        return tv
    
    @classmethod
    def _canHandle(self, sourceFormat, reqFormat):
        return all([formatConverterCls._canHandle(sourceFormat, reqFormat) \
                    for formatConverterCls in self._formatConverterClsList])
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return reduce(lambda l1,l2:l1+l2, [formatConverterCls._getTrackFormatExceptionList() \
                                           for formatConverterCls in cls._formatConverterClsList])

    @classmethod
    def getOutputDescription(self, sourceFormatName):
        return "Combined format converter (converted from '" + sourceFormatName + "')"

#class IterateUniqueValsAndSegmentToStartPointFormatConverter(JoinedFormatConverter):
#    _formatConverterClsList=[IterateUniqueValsFormatConverter, SegmentToStartPointFormatConverter]
#
#    def getOutputDescription(self, sourceFormatName):
#        return "For all categories, with the upstream end point of every segment (converted from '" + sourceFormatName + "')"
#    
#class IterateUniqueValsAndSegmentToMidPointFormatConverter(JoinedFormatConverter):
#    _formatConverterClsList=[IterateUniqueValsFormatConverter, SegmentToMidPointFormatConverter]
#
#    def getOutputDescription(self, sourceFormatName):
#        return "For all categories, with the middle point of every segment (converted from '" + sourceFormatName + "')"
#
#class IterateUniqueValsAndSegmentToEndPointFormatConverter(JoinedFormatConverter):
#    _formatConverterClsList=[IterateUniqueValsFormatConverter, SegmentToEndPointFormatConverter]
#
#    def getOutputDescription(self, sourceFormatName):
#        return "For all categories, with the downstream end point of every segment (converted from '" + sourceFormatName + "')"

