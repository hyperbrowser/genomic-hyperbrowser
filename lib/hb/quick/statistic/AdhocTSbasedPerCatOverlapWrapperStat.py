from gold.track.TrackStructure import TrackStructure
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import MultipleTrackStatistic

class AdhocTSbasedPerCatOverlapWrapperStat(MagicStatFactory):
    '''
    classdocs
    '''
    pass



class AdhocTSbasedPerCatOverlapWrapperStatUnsplittable(MultipleTrackStatistic):
    def _compute(self):
        res = self._children[0].getResult()
        return res

    def _createChildren(self):
        choices_queryTrack = self._kwArgs['choices_queryTrack']
        choices_gsuite = self._kwArgs['choices_gsuite']
        selected_category = self._kwArgs['selected_category']

        import GuiBasedTsFactory
        queryTS = GuiBasedTsFactory.getSingleTrackTS(choices_queryTrack)
        refTS = GuiBasedTsFactory.getTrackListTS(genome, choices_gsuite)

        #trackStructure = TrackStructure()
        #self._tracks

        #self._addChild(AdhocTSbasedPerCatOverlapV2Stat(self._region, trackStructure, **self._kwArgs)