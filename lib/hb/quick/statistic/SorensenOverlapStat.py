from gold.statistic.RawOverlapStat import RawOverlapStat

'''
Created on Apr 4, 2019
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class SorensenOverlapStat(MagicStatFactory):
    '''
    STAT T10
    '''
    pass


class SorensenOverlapStatUnsplittable(Statistic):
    def _compute(self):
        only1, only2, both = [self._children[0].getResult()[key] for key in ['Only1', 'Only2', 'Both']]
        if only1 + only2 + both == 0:
            return 0.0
        return 2.0 * both / (only1 + only2 + 2*both)

    def _createChildren(self):
        self._addChild(RawOverlapStat(self._region, self._track, self._track2))
