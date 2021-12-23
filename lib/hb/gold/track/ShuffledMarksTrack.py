import numpy
from gold.track.SingleRandomizedTrack import SingleRandomizedTrack


class ShuffledMarksTrack(SingleRandomizedTrack):
    @classmethod
    def supportsTrackFormat(cls, origTrackFormat):
        return origTrackFormat.isValued()

    @classmethod
    def supportsOverlapMode(cls, allowOverlaps):
        return True

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands, ids,
                                     edges, weights, extras, region):
        newVals = numpy.copy(vals)
        permutIndexes = numpy.random.permutation(len(newVals))
        newVals = newVals[permutIndexes]

        return starts, ends, newVals, strands, ids, edges, weights, extras
