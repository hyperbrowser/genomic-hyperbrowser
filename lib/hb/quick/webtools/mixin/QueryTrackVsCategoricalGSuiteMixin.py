from gold.description.AnalysisDefHandler import AnalysisDefHandler
from gold.description.AnalysisList import REPLACE_TEMPLATES
from quick.gsuite import GSuiteStatUtils
from quick.statistic.SummarizedInteractionPerTsCatV2Stat import SummarizedInteractionPerTsCatV2StatUnsplittable
from quick.webtools.ts.RandomizedTsWriterTool import RandomizedTsWriterTool


class QueryTrackVsCategoricalGSuiteMixin(object):

    CAT_GSUITE_KEY = 'gsuite'
    CAT_LBL_KEY = 'categoryName'
    SUMMARY_FUNC_DICT = SummarizedInteractionPerTsCatV2StatUnsplittable.functionDict.keys()

    @classmethod
    def getInputBoxNamesForQueryTrackVsCatGSuite(cls):
        return [('Select primary group category value', 'categoryVal'),
                ('Select track to track similarity/distance measure', 'similarityFunc'),
                ('Select summary function for track similarity to rest of suite', 'summaryFunc'),
                ('Type of randomization', 'randType'),
                ('Select summary function groups', 'catSummaryFunc'),
                ('Select MCFDR sampling depth', 'mcfdrDepth'),
                ('Select tail alternative for the hypothesis test', 'tail'),
                ('Randomization algorithm', 'randAlg')]

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
    def getOptionsBoxSimilarityFunc(prevChoices):
        return GSuiteStatUtils.PAIRWISE_STAT_LABELS

    @staticmethod
    def getOptionsBoxSummaryFunc(prevChoices):
        return GSuiteStatUtils.SUMMARY_FUNCTIONS_LABELS

    @staticmethod
    def getOptionsBoxRandType(prevChoices):
        return RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT.keys() + ["Wilcoxon"]

    @staticmethod
    def getOptionsBoxCatSummaryFunc(prevChoices):
        if prevChoices.randType not in ["Wilcoxon"]:
            return SummarizedInteractionPerTsCatV2StatUnsplittable.functionDict.keys()

    @staticmethod
    def getOptionsBoxMcfdrDepth(prevChoices):
        if prevChoices.randType not in ["Wilcoxon"]:
            return AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0]

    @staticmethod
    def getOptionsBoxTail(prevChoices):
            # return ['two.sided', 'less', 'greater']
        return ['right-tail', 'left-tail', 'two-tail']

    @staticmethod
    def getOptionsBoxRandAlg(prevChoices):
        if prevChoices.randType not in ["Wilcoxon"]:
            for definedRandType in RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT.keys():
                if prevChoices.randType == definedRandType:
                    return RandomizedTsWriterTool.RANDOMIZATION_ALGORITHM_DICT[definedRandType].keys()
