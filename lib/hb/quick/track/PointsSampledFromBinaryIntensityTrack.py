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

import numpy
from gold.track.RandomizedTrack import RandomizedTrack
from gold.util.CustomExceptions import IncompatibleTracksError, InvalidRunSpecException
from gold.track.Track import PlainTrack
from gold.track.SegsSampledByIntensityTrack import SegsSampledByIntensityTrack
from collections import OrderedDict
#from quick.util.CommonFunctions import convertTNstrToTNListFormat
from urllib import unquote
from config.Config import IS_EXPERIMENTAL_INSTALLATION
from random import randint, random

class PointsSampledFromBinaryIntensityTrack(SegsSampledByIntensityTrack):
    WORKS_WITH_MINIMAL = False

    def _checkTrackFormat(self, origTV):
        if origTV.trackFormat.isDense() or origTV.trackFormat.isInterval():
            raise IncompatibleTracksError()

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        referenceTV = PlainTrack(self._trackNameIntensity).getTrackView(region) #self._trackNameIntensity based on naming convenience wrt. inheritance

        if referenceTV.trackFormat.isDense():
            raise InvalidRunSpecException('Error: Intensity needs to be a binary (non-dense) track')
        else:
            return self._createRandomizedNumpyArraysFromBinaryIntensity(binLen, starts, ends, vals, strands, ids, edges, weights, extras, referenceTV)

    def _createRandomizedNumpyArraysFromBinaryIntensity(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, referenceTV):
        if len(starts)==0:
            assert len(ends)==0
            return starts, ends, vals, strands, ids, edges, weights, extras

        #elementLengths = ends - starts

        universeStarts = referenceTV.startsAsNumpyArray()
        assert len(universeStarts) >= len(starts)
        assert ends is None or all(ends==starts+1)

        sampledStarts = numpy.random.choice(universeStarts, len(starts), replace=False)
        sampledEnds = None if ends is None else sampledStarts+1

        return sampledStarts, sampledEnds, vals, strands, ids, edges, weights, extras
