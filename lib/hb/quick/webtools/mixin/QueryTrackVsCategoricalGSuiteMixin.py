from gold.track.TrackStructure import TrackStructureV2
from quick.extra.plot import RPlotUtil
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2StatUnsplittable


class QueryTrackVsCategoricalGSuiteMixin(object):

    RANDOMIZABLE_INPUTS = [TrackStructureV2.REF_KEY, TrackStructureV2.QUERY_KEY]

    CAT_GSUITE_KEY = 'gsuite'
    CAT_LBL_KEY = 'categoryName'
    SUMMARY_FUNC_DICT = SummarizedInteractionPerTsCatV2StatUnsplittable.functionDict.keys()
    DIFF_RANK_SUM_CAT_SUMMARY_FUNC_LBL = "Difference of rank averages"

    @classmethod
    def getInputBoxNamesForQueryTrackVsCatGSuite(cls):
        return [('Select primary case label', 'categoryVal'),
                ('Select null model', 'randType'),
                ('Select pairwise similarity measure', 'similarityFunc'),
                ('Select between group summary function', 'catSummaryFunc'),
                ('Select within group summary function', 'summaryFunc'),
                ('Select MCFDR sampling depth', 'mcfdrDepth'),
                ('Select tail alternative for the hypothesis test', 'tail'),
                ('Select preservation and randomization scheme', 'randAlg'),
                ('Randomize reference or case-control tracks?', 'randInput')
                ]

    @classmethod
    def getOptionsBoxCategoryVal(cls, prevChoices):
        if cls._getGSuite(prevChoices) and cls._getCategoryName(prevChoices):
            from quick.multitrack.MultiTrackCommon import getGSuiteFromGalaxyTN
            gsuite = getGSuiteFromGalaxyTN(cls._getGSuite(prevChoices))
            return list(set(gsuite.getAttributeValueList(cls._getCategoryName(prevChoices))))

    @classmethod
    def _getCategoryName(cls, choices):
        return getattr(choices, cls.CAT_LBL_KEY)

    @classmethod
    def _getGSuite(cls, choices):
        return getattr(choices, cls.CAT_GSUITE_KEY)

    @staticmethod
    def getOptionsBoxRandType(prevChoices):
        from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool
        return RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT.keys() + ["Wilcoxon"] + ["T-test"]

    @staticmethod
    def getOptionsBoxSimilarityFunc(prevChoices):
        from quick.gsuite import GSuiteStatUtils
        return GSuiteStatUtils.PAIRWISE_STAT_LABELS

    @classmethod
    def getOptionsBoxCatSummaryFunc(cls, prevChoices):
        if prevChoices.randType not in ["Wilcoxon", "T-test"]:
            return SummarizedInteractionPerTsCatV2StatUnsplittable.functionDict.keys() + \
                   [cls.DIFF_RANK_SUM_CAT_SUMMARY_FUNC_LBL]

    @classmethod
    def getOptionsBoxSummaryFunc(cls, prevChoices):
        if prevChoices.catSummaryFunc not in [cls.DIFF_RANK_SUM_CAT_SUMMARY_FUNC_LBL]:
            from quick.gsuite import GSuiteStatUtils
            return GSuiteStatUtils.SUMMARY_FUNCTIONS_LABELS


    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        if prevChoices.randType not in ["Wilcoxon", "T-test"]:
            from gold.description.AnalysisDefHandler import AnalysisDefHandler
            from gold.description.AnalysisList import REPLACE_TEMPLATES
            return AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0]

    @staticmethod
    def getOptionsBoxTail(prevChoices):
        # return ['two.sided', 'less', 'greater']
        return ['right-tail', 'left-tail', 'two-tail']

    @staticmethod
    def getOptionsBoxRandAlg(prevChoices):
        if prevChoices.randType not in ["Wilcoxon", "T-test"]:
            from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool
            for definedRandType in RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT.keys():
                if prevChoices.randType == definedRandType:
                    return RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT[definedRandType].keys()

    @classmethod
    def getOptionsBoxRandInput(cls, prevChoices):
        if prevChoices.randType not in ["Wilcoxon", "T-test"] and cls.RANDOMIZABLE_INPUTS and \
                len(cls.RANDOMIZABLE_INPUTS) > 1:
            return cls.RANDOMIZABLE_INPUTS


    @classmethod
    def _getSubGSuiteResults(cls, mcResult, galaxyFn, subGSuiteLbl, catSummaryFunc):
        from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2Stat
        from quick.statistic.DiffOfSummarizedRanksPerTsCatV2Stat import DiffOfSummarizedRanksPerTsCatV2Stat
        from quick.util import McEvaluators
        rawNDResultsFile = cls._getNullDistributionFile(galaxyFn, subGSuiteLbl, mcResult)
        testStatLbl = 'TSMC_' + DiffOfSummarizedRanksPerTsCatV2Stat.__name__ if \
            catSummaryFunc == cls.DIFF_RANK_SUM_CAT_SUMMARY_FUNC_LBL else \
            'TSMC_' + SummarizedInteractionPerTsCatV2Stat.__name__
        return [mcResult[testStatLbl],
                mcResult[McEvaluators.PVAL_KEY],
                mcResult[McEvaluators.MEAN_OF_NULL_DIST_KEY],
                mcResult[McEvaluators.SD_OF_NULL_DIST_KEY],
                rawNDResultsFile.getLink("ND {}".format(subGSuiteLbl))]

    @classmethod
    def _getNullDistributionFile(cls, galaxyFn, subGSuiteLbl, mcResult):
        from quick.util import McEvaluators
        from proto.StaticFile import GalaxyRunSpecificFile
        nullRawResults = mcResult[McEvaluators.RAND_RESULTS_KEY]
        rawNDResultsFile = GalaxyRunSpecificFile(["NullDist", subGSuiteLbl, "table.txt"], galaxyFn)
        with rawNDResultsFile.getFile() as f:
            line = "\t".join([str(_) for _ in nullRawResults]) + "\n"
            f.write(line)
        return rawNDResultsFile


    @classmethod
    def _multipleMCResultsToHtmlCore(cls, core, choices, results, galaxyFn):
        from collections import OrderedDict
        core.paragraph('The similarity score for each group is measured as the <b>{}</b> of the "<b>{}</b>".'.format(
            choices.summaryFunc, choices.similarityFunc))
        resTableDict = OrderedDict()
        for subGSuiteLbl, subGSuiteTSResult in results.items():
            resTableDict[subGSuiteLbl] = cls._getSubGSuiteResults(subGSuiteTSResult.getResult(), galaxyFn,
                                                                  subGSuiteLbl, choices.catSummaryFunc)
        columnNames = ["GSuite index", choices.catSummaryFunc, "P-value", "Mean score for null distribution",
                       "Std. deviation of score for null distribution", "Null distribution"]
        from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
        addTableWithTabularAndGsuiteImportButtons(core, choices, galaxyFn, 'table', resTableDict, columnNames)

        pvals = [x[1] for x in resTableDict.values()]
        nameList = ["Monte_Carlo", "qqplot.png"]
        cls._addQQPlot(core, pvals, nameList, galaxyFn)

    @classmethod
    def _writeInfo(cls, benchmark, choices, results, fn):
        from os import linesep
        from quick.util import McEvaluators
        strOut = ""
        strOut += "benchmark={}".format(benchmark) + linesep
        strOut += "method={}".format(cls._determineMethod(choices)) + linesep
        strOut += "simMeasure={}".format(choices.similarityFunc) + linesep
        strOut += "catSummaryFunc={}".format(choices.catSummaryFunc) + linesep
        if choices.randType == "Wilcoxon" or choices.randType == "T-test":
            for key, val in results.iteritems():
                strOut += "pval_{}={}".format(key, val.getResult()['p.value']) + linesep
        else:
            for key, res in results.items():
                strOut += "pval_{}={}".format(key, res.getResult()[McEvaluators.PVAL_KEY]) + linesep

        with open(fn, "wt") as f:
            f.write(strOut)

    @classmethod
    def _determineMethod(cls, choices):
        if choices.catSummaryFunc not in [cls.DIFF_RANK_SUM_CAT_SUMMARY_FUNC_LBL]:
            if choices.randType == "Wilcoxon":
                return 1
            elif choices.randType == 'Within tracks':
                if choices.randAlg == \
                        'Permute segments and sampled inter-segment regions (size of inter-segment regions is random)':
                    if choices.randInput == "reference":
                        return 2
                    else:
                        return 3
            elif choices.randType == 'Between tracks':
                if choices.randAlg == 'Shuffle between tracks':
                    if choices.randInput == "case-control":
                        return 4
        else:
            if choices.randInput == "reference":
                if choices.randAlg == \
                        'Permute segments and sampled inter-segment regions (size of inter-segment regions is random)':

                    return 6
            elif choices.randType == 'Between tracks':
                if choices.randAlg == 'Shuffle between tracks':
                    return 5

        return -1

    @classmethod
    def _addQQPlot(cls, core, pvals, nameList, galaxyFn):
        import numpy as np
        from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
        n = len(pvals)
        theoreticalVals = np.random.uniform(0, 1, n)
        plotOutput = GalaxyRunSpecificFile(nameList, galaxyFn)
        plotOutput.openRFigure()
        mainTitle = 'Uniform Q-Q Plot of the P-values'
        xTitle = 'Theoretical Quantiles'
        yTitle = 'Sample Quantiles'
        RPlotUtil.drawQQPlot(theoreticalVals, pvals, [0, 1], [0, 1], mainTitle, xTitle, yTitle)
        RPlotUtil.rDevOff()
        core.divBegin()
        core.image(plotOutput.getURL())
        core.divEnd()
