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

from gold.origdata.GESourceWrapper import GESourceWrapper
from gold.util.CustomExceptions import NotSupportedError
from gold.track.TrackFormat import TrackFormat
from copy import copy

class GEFilter(GESourceWrapper):
    def __init__(self, geSource):
        GESourceWrapper.__init__(self, geSource)
        self._geIter = None    

    def __iter__(self):
        self = copy(self)
        
        #does not support function, partitions and points:
        if (False in [attrs in self._geSource.getPrefixList() for attrs in ['start', 'end']]):
            raise NotSupportedError('Binning file must be segments. Current file format: ' + \
                                    TrackFormat.createInstanceFromPrefixList(self._geSource.getPrefixList(), \
                                                                             self._geSource.getValDataType(), \
                                                                             self._geSource.getValDim(), \
                                                                             self._geSource.getEdgeWeightDataType(), \
                                                                             self._geSource.getEdgeWeightDim()).getFormatName() )

        self._geIter = self._geSource.__iter__()
        return self

    def  __len__(self):
        return sum(1 for i in self)