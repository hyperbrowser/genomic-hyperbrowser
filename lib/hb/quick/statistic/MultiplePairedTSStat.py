from collections import OrderedDict

from quick.statistic.PairedTSStat import PairedTSStat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class MultiplePairedTSStat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


#class MultiplePairedTSStatSplittable(StatisticSumResSplittable):
#    pass

class MultiplePairedTSStatUnsplittable(StatisticV2):

    def _compute(self):

        ts = self._trackStructure._copyTreeStructure()
        for key, pairedTS in ts.iteritems():
            pairedTS.result = self._childrenDict[key].getResult().result

        return ts

    def _createChildren(self):
        self._childrenDict = OrderedDict()
        for key, pairedTS in self._trackStructure.iteritems():
            self._childrenDict[key] = PairedTSStat(self._region, pairedTS, **self._kwArgs)
        #TODO: traverse TrackStructure, for each pairedTS run raw stat. To handle multiple categories
        #But, where to save the chidren stats? TrackStructure? Execute a stat only when .result of a node is called?
        #For now just assume each ts child node is a PairedTS