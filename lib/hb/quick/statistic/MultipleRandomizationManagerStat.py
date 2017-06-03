from collections import OrderedDict

from gold.statistic.MCSamplingStat import MCSamplingStatUnsplittable
from quick.mcsampler.GenericMCSampler import GenericMCSampler
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.util.McEvaluators import *
from quick.mcsampler.NaiveMCSampler import NaiveMCSampler


class MultipleRandomizationManagerStat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class MultipleRandomizationManagerStatSplittable(StatisticSumResSplittable):
#    pass

class MultipleRandomizationManagerStatUnsplittable(StatisticV2):

    def _init(self, evaluatorFunc, mcSamplerClass, tail, rawStatistic, maxSamples, **kwArgs):
        if type(evaluatorFunc) is str:
            evaluatorFunc = globals()[evaluatorFunc]
        self._evaluatorFunc = evaluatorFunc

        if isinstance(mcSamplerClass, basestring):
            mcSamplerClass = globals()[mcSamplerClass]
        self._mcSamplerClass = mcSamplerClass

        self._tail = tail
        self._rawStatistic = self.getRawStatisticClass(rawStatistic)  # just to extract name
        if kwArgs.get('minimal') == True:
            self._maxSamples = 1
        else:
            self._maxSamples = int(maxSamples)

        self._kwArgs = kwArgs

    def compute(self):

        mcSamplersDict = self._computeSamples()
        for hypothesisKey, hypothesisTS in self._trackStructure.iteritems():
            currentMcSampler = mcSamplersDict[hypothesisKey]
            hypothesisTS.result = self._evaluatorFunc(currentMcSampler.getAllResults(), self._tail, self._rawStatistic.__name__)

        return self._trackStructure


    def _computeSamples(self):
        mcSamplersDict = OrderedDict()
        for i in xrange(self._maxSamples):
            for hypothesisKey, hypothesisTS in self._trackStructure.iteritems():
                hypothesisTS.updateRandIndex(i)
                if hypothesisKey not in mcSamplersDict:
                    currentSampler = self._mcSamplerClass(
                        self._rawStatistic,
                        self._region,
                        hypothesisTS,
                        GenericMCSampler,
                        **self._kwArgs
                    )
                    mcSamplersDict[hypothesisKey] = currentSampler
                    currentSampler.computeRealResult()
                else:
                    currentSampler = mcSamplersDict[hypothesisKey]

                currentSampler.computeAdditionalRandomResult()
        return mcSamplersDict

    def createChildren(self):
        pass