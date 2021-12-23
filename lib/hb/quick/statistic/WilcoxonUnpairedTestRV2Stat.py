from collections import deque

from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class WilcoxonUnpairedTestRV2Stat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


# class WilcoxonUnpairedTestRV2StatSplittable(StatisticSumResSplittable):
#    pass

class WilcoxonUnpairedTestRV2StatUnsplittable(StatisticV2):
    TAIL_ALTERNATIVE_MAP = dict(
        [('right-tail', 'greater'),
         ('left-tail', 'less'),
         ('two-tail', 'two.sided')]
    )

    def _init(self, alternative="right-tail", primaryCatVal=None, **kwArgs):
        self._alternative = self.TAIL_ALTERNATIVE_MAP[alternative]
        self._kwArgs = kwArgs
        self._primaryCatVal = primaryCatVal

    def _compute(self):
        tsResult = self._children[0].getResult()
        groups = deque()
        scores = deque()
        for group, val in tsResult.items():
            vals = val.getResult()
            if group == self._primaryCatVal:
                scores.extendleft(vals)
                groups.extendleft([group] * len(vals))
            else:
                scores.extend(vals)
                groups.extend([group] * len(vals))

        assert groups, "Must have categories"
        assert scores, "Must have raw scores"

        from proto.RSetup import robjects
        from rpy2.robjects import FloatVector, Formula, StrVector
        wilcoxTest = robjects.r['wilcox.test']
        x = StrVector(list(groups))
        y = FloatVector(list(scores))
        fmla = Formula('y ~ x')
        env = fmla.environment
        env['x'] = x
        env['y'] = y

        wilcoxResult = wilcoxTest(fmla, alternative=self._alternative, paired=False)
        # wilcoxResults.names = ['statistic' 'parameter' 'p.value' 'null.value' 'alternative' 'method', 'data.name']
        print("Setting results")
        tsResult.setResult(dict([(wilcoxResult.names[i], wilcoxResult[i]) for i in xrange(len(wilcoxResult.names))]))
        return tsResult

    def _createChildren(self):
        self._addChild(SummarizedInteractionPerTsCatV2Stat(
            self._region, self._trackStructure, summaryFunc='raw', **self._kwArgs))
