from gold.track.TrackStructure import TrackStructureV2
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2StatUnsplittable, \
    SummarizedInteractionPerTsCatV2Stat


class QueryTrackVsCategoricalGSuiteMixin(object):

    RANDOMIZABLE_INPUTS = [TrackStructureV2.REF_KEY, TrackStructureV2.QUERY_KEY]

    CAT_GSUITE_KEY = 'gsuite'
    CAT_LBL_KEY = 'categoryName'
    SUMMARY_FUNC_DICT = SummarizedInteractionPerTsCatV2StatUnsplittable.functionDict.keys()

    @classmethod
    def getInputBoxNamesForQueryTrackVsCatGSuite(cls):
        return [('Select primary group category value', 'categoryVal'),
                ('Type of randomization', 'randType'),
                ('Select track to track similarity/distance measure', 'similarityFunc'),
                ('Select summary function for track similarity to rest of suite', 'summaryFunc'),
                ('Select summary function groups', 'catSummaryFunc'),
                ('Select MCFDR sampling depth', 'mcfdrDepth'),
                ('Select tail alternative for the hypothesis test', 'tail'),
                ('Randomization algorithm', 'randAlg'),
                ('Randomized input (for MC)', 'randInput')
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
        return RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT.keys() + ["Wilcoxon"]

    @staticmethod
    def getOptionsBoxSimilarityFunc(prevChoices):
        from quick.gsuite import GSuiteStatUtils
        return GSuiteStatUtils.PAIRWISE_STAT_LABELS

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):
        from quick.gsuite import GSuiteStatUtils
        return GSuiteStatUtils.SUMMARY_FUNCTIONS_LABELS

    @staticmethod
    def getOptionsBoxCatSummaryFunc(prevChoices):
        if prevChoices.randType not in ["Wilcoxon"]:
            return SummarizedInteractionPerTsCatV2StatUnsplittable.functionDict.keys()


    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        if prevChoices.randType not in ["Wilcoxon"]:
            from gold.description.AnalysisDefHandler import AnalysisDefHandler
            from gold.description.AnalysisList import REPLACE_TEMPLATES
            return AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0]

    @staticmethod
    def getOptionsBoxTail(prevChoices):
        # return ['two.sided', 'less', 'greater']
        return ['right-tail', 'left-tail', 'two-tail']

    @staticmethod
    def getOptionsBoxRandAlg(prevChoices):
        if prevChoices.randType not in ["Wilcoxon"]:
            from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool
            for definedRandType in RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT.keys():
                if prevChoices.randType == definedRandType:
                    return RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT[definedRandType].keys()

    @classmethod
    def getOptionsBoxRandInput(cls, prevChoices):
        if prevChoices.randType not in ["Wilcoxon"] and cls.RANDOMIZABLE_INPUTS and \
                len(cls.RANDOMIZABLE_INPUTS) > 1:
            return cls.RANDOMIZABLE_INPUTS


    @classmethod
    def _getSubGSuiteResults(cls, mcResult, galaxyFn, subGSuiteLbl):
        from quick.util import McEvaluators
        rawNDResultsFile = cls._getNullDistributionFile(galaxyFn, mcResult)
        return [mcResult['TSMC_' + SummarizedInteractionPerTsCatV2Stat.__name__],
                mcResult[McEvaluators.PVAL_KEY],
                mcResult[McEvaluators.MEAN_OF_NULL_DIST_KEY],
                mcResult[McEvaluators.SD_OF_NULL_DIST_KEY],
                rawNDResultsFile.getLink("ND {}".format(subGSuiteLbl))]

    @classmethod
    def _getNullDistributionFile(cls, galaxyFn, mcResult):
        from quick.util import McEvaluators
        from proto.StaticFile import GalaxyRunSpecificFile
        nullRawResults = mcResult[McEvaluators.RAND_RESULTS_KEY]
        rawNDResultsFile = GalaxyRunSpecificFile(["NullDist", "table.txt"], galaxyFn)
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
                                                                    subGSuiteLbl)
        columnNames = ["GSuite index", choices.catSummaryFunc, "P-value", "Mean score for null distribution",
                       "Std. deviation of score for null distribution", "Null distribution"]
        from quick.gsuite.GSuiteHbIntegration import addTableWithTabularAndGsuiteImportButtons
        addTableWithTabularAndGsuiteImportButtons(core, choices, galaxyFn, 'table', resTableDict, columnNames)