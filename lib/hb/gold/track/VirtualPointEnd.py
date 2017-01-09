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

from gold.track.VirtualNumpyArray import VirtualNumpyArray

class VirtualPointEnd(VirtualNumpyArray):
    def __init__(self, startArray):
        VirtualNumpyArray.__init__(self)
        self._startArray = startArray
        
    #def __getitem__(self, key):
    #    return self._startArray[key] + 1
    #
    #def __getslice__(self, i, j):
    #    return VirtualPointEnd(self._startArray[i:j])
    
    #To support lazy loading, i.e. to not load the modified array in the __init__ method of TrackView
    def __len__(self):
        return len(self._startArray)
    
    def _asNumpyArray(self):
        return self._startArray + 1