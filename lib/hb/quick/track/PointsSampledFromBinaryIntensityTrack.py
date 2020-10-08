import numpy

from gold.track.SingleRandomizedTrack import SingleRandomizedTrack
from gold.util.CustomExceptions import InvalidRunSpecException
from gold.track.Track import PlainTrack
from quick.util.CommonFunctions import convertTNstrToTNListFormat


class PointsSampledFromBinaryIntensityTrack(SingleRandomizedTrack):
    WORKS_WITH_MINIMAL = False

    def _init(self, origTrack, randIndex, trackNameUniverse="", **kwArgs):
        self._trackNameUniverse = convertTNstrToTNListFormat(trackNameUniverse)

    @classmethod
    def supportsTrackFormat(cls, origTrackFormat):
        return origTrackFormat.isPoints()

    @classmethod
    def supportsOverlapMode(cls, allowOverlaps):
        return not allowOverlaps

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges,
                                     weights, extras, region):
        universeTV = PlainTrack(self._trackNameUniverse).getTrackView(region)

        if universeTV.trackFormat.isDense():
            raise InvalidRunSpecException('Error: Universe needs to be a binary (non-dense) track')
        else:
            return self._createRandomizedNumpyArraysFromBinaryUniverse(
                binLen, starts, ends, vals, strands, ids, edges, weights, extras, universeTV)

    @classmethod
    def _createRandomizedNumpyArraysFromBinaryUniverse(cls, starts, ends, vals, strands, ids,
                                                       edges, weights, extras, universeTV):
        if len(starts) == 0:
            assert len(ends) == 0
            return starts, ends, vals, strands, ids, edges, weights, extras

        universeStarts = universeTV.startsAsNumpyArray()
        assert len(universeStarts) >= len(starts)
        assert ends is None or all(ends == starts + 1)

        sampledStarts = numpy.random.choice(universeStarts, len(starts), replace=False)
        sampledStarts.sort()
        sampledEnds = None if ends is None else sampledStarts+1

        return sampledStarts, sampledEnds, vals, strands, ids, edges, weights, extras
