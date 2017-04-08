from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic

class [[%tabstop1:X]]Stat(MagicStatFactory):
    pass

#class [[%tabstop1:X]]StatSplittable(StatisticSumResSplittable):
#    pass
            
class [[%tabstop1:X]]StatUnsplittable(Statistic):    
    def _compute(self):
        pass
    
    def _createChildren(self):
        pass
