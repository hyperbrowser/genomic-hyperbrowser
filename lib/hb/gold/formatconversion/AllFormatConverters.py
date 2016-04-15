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

from gold.formatconversion.FormatConverter import TrivialFormatConverter
from gold.formatconversion.SegmentToPointFormatConverter import SegmentToStartPointFormatConverter, \
    SegmentToMidPointFormatConverter, SegmentToEndPointFormatConverter
from gold.util.CommonFunctions import getClassName

ALL_CONVERTERS = [TrivialFormatConverter, SegmentToStartPointFormatConverter, SegmentToMidPointFormatConverter, \
                  SegmentToEndPointFormatConverter]

def getFormatConverters(sourceFormat, reqFormat):
    assert(reqFormat!=None)
    allObjects = [cls(sourceFormat, reqFormat) for cls in ALL_CONVERTERS]
    return [x for x in allObjects if x is not None]

def getFormatConverterByName(converterClassName):
    formatConverter = globals()[converterClassName]()
    assert( formatConverter.__class__ in ALL_CONVERTERS )
    return formatConverter