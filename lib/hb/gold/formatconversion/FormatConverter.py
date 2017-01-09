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

from gold.util.CustomExceptions import AbstractClassError

class FormatConverter(object):
    VERSION = '1.0'
    
    def __new__(cls, sourceFormat=None, reqFormat=None):
        if sourceFormat is None: #then we have explicitly created a subclass
            return object.__new__(cls)
        else:
            if cls.canHandle(sourceFormat, reqFormat):
                return object.__new__(cls)
            else:
                return None
        
    def __init__(self, sourceFormat=None, reqFormat=None):
        self._sourceFormat = sourceFormat
        self._reqFormat = reqFormat

    @classmethod
    def canHandle(cls, sourceFormat, reqFormat):
        return cls._canHandle(sourceFormat, reqFormat) and \
            reqFormat.isCompatibleWith(sourceFormat, cls._getTrackFormatExceptionList())

    @classmethod
    def _canHandle(cls, sourceFormat, reqFormat):
        raise AbstractClassError
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return []
            
class TrivialFormatConverter(FormatConverter):
    def getOutputDescription(self, sourceFormatName):
        return "Original format ('" + sourceFormatName + "')"
    
    @classmethod
    def convert(cls, trackView):
        return trackView
    
    @classmethod
    def _canHandle(cls, sourceFormat, reqFormat):
        return True
    
    @classmethod
    def _getTrackFormatExceptionList(cls):
        return []
