import math

from gold.statistic.RawOverlapStat import RawOverlapStat

'''
Created on Apr 4, 2019
'''

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic


class PearsonCorrelationStat(MagicStatFactory):
    '''
    STAT T11
    '''
    pass


# class RatioOfOverlapToUnionStatSplittable(StatisticSumResSplittable):
#    pass

class PearsonCorrelationStatUnsplittable(Statistic):
    def _compute(self):
        n,o1,o2,b = [self._children[0].getResult()[key] for key in ['Neither','Only1', 'Only2', 'Both']]
        if (b+o2)*(n+o1)*(b+o1)*(n+o2) == 0:
            return 0.0
        return float(b*n-o2*o1) / math.sqrt((b+o2)*(n+o1)*(b+o1)*(n+o2))

    def _createChildren(self):
        self._addChild(RawOverlapStat(self._region, self._track, self._track2))
