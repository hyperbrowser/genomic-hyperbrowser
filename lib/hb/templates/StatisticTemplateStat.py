from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic

class StatisticTemplateStat(MagicStatFactory):
    "Statistic description"
    pass

class StatisticTemplateStatUnsplittable(Statistic):
    def _compute(self):
        pass
    
    def _createChildren(self):
        pass

#from gold.statistic.Statistic import StatisticSumResSplittable
#class StatisticTemplateStatSplittable(StatisticSumResSplittable):
#   pass
