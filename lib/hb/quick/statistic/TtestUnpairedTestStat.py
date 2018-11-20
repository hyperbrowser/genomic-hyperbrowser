from collections import deque

from gold.application.LogSetup import logMessage
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
from quick.statistic.StatisticV2 import StatisticV2
from gold.statistic.MagicStatFactory import MagicStatFactory


class TtestUnpairedTestStat(MagicStatFactory):
    """
    Please insert docs for the statistic here.
    """
    pass


# class WilcoxonUnpairedTestRV2StatSplittable(StatisticSumResSplittable):
#    pass

class TtestUnpairedTestStatUnsplittable(StatisticV2):
    TAIL_ALTERNATIVE_MAP = dict(
        [('right-tail', 'greater'),
         ('left-tail', 'less'),
         ('two-tail', 'two.sided')]
    )

    def _init(self, alternative="right-tail", primaryCatVal=None, **kwArgs):
        self._alternative = self.TAIL_ALTERNATIVE_MAP[alternative]
        self._kwArgs = kwArgs
        self._primaryCatVal = primaryCatVal

    from gold.util.CommonFunctions import repackageException
    from gold.util.CustomExceptions import ShouldNotOccurError
    @repackageException(Exception, ShouldNotOccurError)
    def _compute(self):
        tsResult = self._children[0].getResult()
        groups = deque()
        scores = deque()
        for group, val in tsResult.items():
            vals = val.getResult()
            #print("Group/val: %s, %s" % (group, vals))
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
        tTest = robjects.r['t.test']
        x = StrVector(list(groups))
        y = FloatVector(list(scores))

        print("x: " + str(x))
        print("y: " + str(y))

        print("""
        x = c(%s)
        y = c(%s)
        f = Formula('y ~ x')
        env = f$environment
        result = t.test(formula, paired=False)
        """ % (', '.join("'" + str(element) + "'" for element in x), ', '.join(str(element) for element in y)))

        fmla = Formula('y ~ x')
        env = fmla.environment
        env['x'] = x
        env['y'] = y

        tResult = tTest(fmla, alternative=self._alternative, paired=False)
        #tResult = tTest(FloatVector([1.0, 1.2, 1.3]), FloatVector([1.2, 1.4, 1.5]), equal=True)
        print("Names: " + str(tResult.names))
        # wilcoxResults.names = ['statistic' 'parameter' 'p.value' 'null.value' 'alternative' 'method', 'data.name']
        tsResult.setResult(dict([(tResult.names[i], tResult[i]) for i in xrange(len(tResult.names))]))
        return tsResult

    def _createChildren(self):
        self._addChild(SummarizedInteractionPerTsCatV2Stat(
            self._region, self._trackStructure, summaryFunc='raw', **self._kwArgs))
