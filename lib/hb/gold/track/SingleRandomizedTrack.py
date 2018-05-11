import numpy

from abc import ABCMeta, abstractmethod

from gold.track.RandomizedTrack import RandomizedTrack
from gold.track.TrackView import TrackView


class SingleRandomizedTrack(RandomizedTrack):
    __metaclass__ = ABCMeta

    def _getRandTrackView(self, region):
        origTV = self._origTrack.getTrackView(region)

        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._createRandomizedNumpyArrays(
                len(origTV.genomeAnchor), origTV.startsAsNumpyArray(),
                origTV.endsAsNumpyArray(), origTV.valsAsNumpyArray(),
                origTV.strandsAsNumpyArray(), origTV.idsAsNumpyArray(),
                origTV.edgesAsNumpyArray(), origTV.weightsAsNumpyArray(),
                origTV.allExtrasAsDictOfNumpyArrays(), region)

        starts, ends, vals, strands, ids, edges, weights, extras = \
            self._undoTrackViewChanges(starts, ends, vals, strands, ids,
                                       edges, weights, extras, origTV)

        return TrackView(origTV.genomeAnchor, starts, ends, vals, strands, ids, edges, weights,
                         origTV.borderHandling, origTV.allowOverlaps, extraLists=extras)

    @classmethod
    def _undoTrackViewChanges(cls, starts, ends, vals, strands, ids,
                              edges, weights, extras, origTV):
        if origTV.trackFormat.isPoints():
            ends = None

        elif origTV.trackFormat.isPartitionOrStepFunction():
            ends = numpy.append([0], ends)
            starts = None

        if starts is not None:
            starts += origTV.genomeAnchor.start

        if ends is not None:
            ends += origTV.genomeAnchor.start

        return starts, ends, vals, strands, ids, edges, weights, extras

    @abstractmethod
    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands,
                                     ids, edges, weights, extras, region):
        pass
