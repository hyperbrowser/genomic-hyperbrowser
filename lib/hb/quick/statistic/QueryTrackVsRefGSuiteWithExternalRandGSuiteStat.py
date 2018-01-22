from gold.track.TSResult import TSResult
from gold.track.TrackStructure import TrackStructureV2
from quick.statistic.MultitrackSummarizedInteractionWithOtherTracksV2Stat import \
    MultitrackSummarizedInteractionWithOtherTracksV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat


class QueryTrackVsRefGSuiteWithExternalRandGSuiteStat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class QueryTrackVsRefGSuiteWithExternalRandGSuiteStatSplittable(StatisticSumResSplittable):
#    pass

class QueryTrackVsRefGSuiteWithExternalRandGSuiteStatUnsplittable(StatisticV2):

    def _init(self, **kwArgs):
        assert TrackStructureV2.QUERY_KEY in self._trackStructure, \
            'Missing %s node in the track structure' % TrackStructureV2.QUERY_KEY
        assert TrackStructureV2.REF_KEY in self._trackStructure, \
            'Missing %s node in the track structure' % TrackStructureV2.REF_KEY
        assert 'randQuery' in self._trackStructure, \
            'Missing randQuery node in the track structure'
        self._kwArgs = kwArgs

    def _compute(self):
        tsResult = TSResult(self._trackStructure)
        tsResult['real'] = self._childrenDict['real'].getResult()
        tsResult['rand'] = self._childrenDict['rand'].getResult()
        return tsResult

    def _createChildren(self):
        realTS = TrackStructureV2()
        realTS[TrackStructureV2.QUERY_KEY] = self._trackStructure[TrackStructureV2.QUERY_KEY]
        realTS[TrackStructureV2.REF_KEY] = self._trackStructure[TrackStructureV2.REF_KEY]
        randTS = TrackStructureV2()
        randTS[TrackStructureV2.QUERY_KEY] = self._trackStructure['randQuery']
        randTS[TrackStructureV2.REF_KEY] = self._trackStructure[TrackStructureV2.REF_KEY]

        self._childrenDict = dict()
        self._childrenDict['real'] = self._addChild(SummarizedInteractionPerTsCatV2Stat(
            self._region, realTS, **self._kwArgs))
        self._childrenDict['rand'] = self._addChild(MultitrackSummarizedInteractionWithOtherTracksV2Stat(
            self._region, randTS, **self._kwArgs))
