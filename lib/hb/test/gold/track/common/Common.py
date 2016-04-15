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

#from gold.track.TrackFormat import TrackFormat
#from numpy import array
#
#def _appendDict(dict, key, value):
#    if type(value) == type([]) or type(value) == type(array([])) or value == True:
#        dict[key] = value
#
#def createTrackFormat(start, end, val, strand):
#    dict = {}
#    _appendDict(dict, 'start', start)
#    _appendDict(dict, 'end', end)
#    _appendDict(dict, 'val', val)
#    _appendDict(dict, 'strand', strand)
#    return TrackFormat(dict)