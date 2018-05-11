import numpy
from gold.track.RandomizedTrack import RandomizedTrack


class ShuffledMarksTrack(RandomizedTrack):
    @classmethod
    def supportsTrackFormat(cls, origTrackFormat):
        return origTrackFormat.isValued()

    @classmethod
    def supportsOverlapMode(cls, allowOverlaps):
        return True

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids, edges, weights, extras, region):
        newVals = numpy.copy(vals)
        numpy.random.shuffle(newVals)

        return starts, ends, newVals, strands, ids, edges, weights, extras
