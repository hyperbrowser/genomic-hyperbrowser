from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.RawDataStat import RawDataStat
from gold.statistic.Statistic import Statistic
from gold.track.TrackFormat import TrackFormatReq
from gold.track.TrackView import TrackView
from quick.statistic.BinSizeStat import BinSizeStat


class NoisyPointTrackGenerationStat(MagicStatFactory):
    '''Generates an output track based on the input track, using separate point probabilities where the input track had points or not
    '''
    pass

class NoisyPointTrackGenerationStatUnsplittable(Statistic):
    def _init(self, keepOnesProb=None, introduceZerosProb=None, **kwArgs):
        self._keepOnesProb = float(keepOnesProb)
        self._introduceZerosProb = float(introduceZerosProb)

    def _compute(self):
        tv = self._rawData.getResult()
        binSize = self._binSizeStat.getResult()
        points = tv.startsAsNumpyArray()
        sampler = SparseSampling(binSize, points, self._keepOnesProb, self._introduceZerosProb)
        sampledStartsArray = sampler.get_samples()
        outTv = TrackView(self._region, sampledStartsArray, None, None,None,None,None,None,borderHandling='crop',allowOverlaps=False)
        return TrackView

    def _createChildren(self):
        self._rawData = self._addChild(RawDataStat(self._region, self._track, TrackFormatReq(dense=False, interval=False)))
        self._binSizeStat = self._addChild(BinSizeStat(self._region, self._track))


import numpy as np
import numpy.random


class SparseSampling:
    def __init__(self, bin_size, ones, ones_prob, zeros_prob):
        self._bin_size = bin_size
        self._ones = ones
        self._ones_prob = ones_prob
        self._zeros_prob = zeros_prob

    def sample_ones(self):
        if self._ones.size==0:
            return numpy.array([])
        poisson_lambda = self._ones.size*self._ones_prob
        N = numpy.random.poisson(poisson_lambda, 1)
        samples = numpy.random.choice(self._ones, N, replace=False)
        return samples

    def sample_zeros(self):
        poisson_lambda = self._bin_size * self._zeros_prob
        N = numpy.random.poisson(poisson_lambda, 1)
        samples = numpy.random.randint(0, self._bin_size, N)
        s = set(samples)-set(self._ones)
        return np.array(list(s), dtype="int")

    def get_samples(self):
        ones = self.sample_ones()
        zeros = self.sample_zeros()
        a = np.concatenate([ones, zeros])
        a.sort()
        return a

