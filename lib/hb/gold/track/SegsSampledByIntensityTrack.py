import numpy

from gold.track.SingleRandomizedTrack import SingleRandomizedTrack
from gold.util.CustomExceptions import InvalidRunSpecException
from gold.track.Track import PlainTrack
from quick.util.CommonFunctions import convertTNstrToTNListFormat


class SegsSampledByIntensityTrack(SingleRandomizedTrack):
    WORKS_WITH_MINIMAL = False

    def _init(self, origTrack, randIndex, trackNameIntensity="", **kwArgs):
        self._trackNameIntensity = convertTNstrToTNListFormat(trackNameIntensity)

    @classmethod
    def supportsTrackFormat(cls, origTrackFormat):
        return origTrackFormat.isPoints()

    @classmethod
    def supportsOverlapMode(cls, allowOverlaps):
        return not allowOverlaps

    def _createRandomizedNumpyArrays(self, binLen, starts, ends, vals, strands,
                                     ids, edges, weights, extras, region):
        intensityTV = PlainTrack(self._trackNameIntensity).getTrackView(region)
        if len(intensityTV.valsAsNumpyArray())==0:
            raise InvalidRunSpecException(
                'Error: No intensity data available for sampling randomized locations in region' +
                str(region) +
                '. Please check that the intensity track was created with the same main track '
                'that is being randomized in this analysis.')

        # # Dependence on origRegion is not nice, but not a big problem..
        # intensityTV = PlainTrack(self._trackNameIntensity).getTrackView(self._origRegion)

        if intensityTV.trackFormat.isDense():
            assert intensityTV.trackFormat.isValued('number')
            return self._createRandomizedNumpyArraysFromIntensityFunction(
                binLen, starts, ends, vals, strands, ids, edges, weights, extras, intensityTV)
        else:
            raise NotImplementedError

    def _createRandomizedNumpyArraysFromIntensityFunction(self, binLen, starts, ends, vals,
                                                          strands, ids, edges, weights,
                                                          extras, intensityTV):
        """Assumes function values are proportional to prior probabilities"""

        if len(starts)==0:
            assert len(ends)==0
            return starts, None, vals, strands, ids, edges, weights, extras

        # Permute vals and strands. Later also segment lengths..
        if vals is not None or strands is not None:
            permutedIndexes = numpy.random.permutation(max(len(starts), len(ends)))
            if vals is not None:
                vals = vals[permutedIndexes]
            if strands is not None:
                strands = strands[permutedIndexes]
            if ids is not None:
                ids = ids[permutedIndexes]
            if edges is not None:
                edges = edges[permutedIndexes]
            if weights is not None:
                weights = weights[permutedIndexes]
            for key in extras:
                extras[key] = extras[key][permutedIndexes]

        # Make the cumulative distribution of prior along the bin, which is what we will
        # sample from.
        intensityVals = intensityTV.valsAsNumpyArray()
        cumulative = numpy.add.accumulate( intensityVals )
        cumulative = cumulative / cumulative[-1]  # normalize

        # Sample positions based on cumulative distribution. Iteratively sample new positions
        # and remove overlap.
        sampledPositions = numpy.array([],dtype='i')
        numTries = 0
        while len(sampledPositions) < len(starts):
            numTries+=1
            if numTries > 200:
                raise RuntimeError(
                    'More than 200 tries at drawing random numbers from intensity. Trying to draw '
                    + str(len(starts)) + ' non-overlapping points among ' + str(len(cumulative)) +
                    ' positions, still lacking ' + str(len(starts)-len(sampledPositions)) +
                    ' points.')

            numRemainingSamples = len(starts) - len(sampledPositions)
            sampledProbs = numpy.random.rand( numRemainingSamples)  # fixme: includes 1?

            newSampledPositions = cumulative.searchsorted( sampledProbs)  # fixme: +/-1 here..
            sampledPositions = numpy.append( sampledPositions, newSampledPositions)
            sampledPositions = numpy.unique(sampledPositions)

        # Handle segments, by simply permuting original segment lengths and add these back
        # to new start positions
        # fixme: Must include overlap handling for segment case and be put into the iterative
        #        sampling..
        # fixme: Must also remove segments crossing bin border..
        # segLens = ends - starts
        # numpy.random.shuffle(segLens)
        # newEnds = sampledPositions + segLens
        # return sampledPositions, newEnds, None, None

        return sampledPositions, None, vals, strands, ids, edges, weights, extras
