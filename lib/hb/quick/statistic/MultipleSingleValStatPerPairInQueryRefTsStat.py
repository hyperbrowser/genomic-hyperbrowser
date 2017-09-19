from gold.track.TrackStructure import TrackStructureV2
from quick.statistic.GenericResultsCombinerStat import GenericResultsCombinerStat
from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultipleSingleValStatPerPairInQueryRefTsStat(MagicStatFactory):
    """
    For a track structure that has query and reference sub-trackstuctures, create a new track structure that holds all
    pairs (query, reference) and run all stats given in rawStatistics. The result for each pair is a dict stat->result
    """
    pass


#class MultipleSingleValStatPerPairInQueryRefTsStatSplittable(StatisticSumResSplittable):
#    pass

class MultipleSingleValStatPerPairInQueryRefTsStatUnsplittable(StatisticV2):

    def _compute(self):
        listOfPairTSs = [child.getResult() for child in self._children]
        tsWithResults = TrackStructureV2()
        for i,pairTS in enumerate(listOfPairTSs):
            tsWithResults[str(i)] = pairTS

        return tsWithResults

    def _createChildren(self):

        #reference is set first (as query) here because single track stats are always ran on the query track
        #make sure to handle this in the results
        pairedTS = self._trackStructure['query'].makePairwiseCombinations(self._trackStructure['reference'])
        for pairTSKey in pairedTS:
            self._addChild(PairedTSStat(self._region, pairedTS[pairTSKey], pairedTsRawStatistic=GenericResultsCombinerStat, **self._kwArgs))