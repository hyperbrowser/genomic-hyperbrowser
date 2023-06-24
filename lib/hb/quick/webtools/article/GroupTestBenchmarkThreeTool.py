from proto.tools.GeneralGuiTool import HistElement
from quick.webtools.misc.GroupTestBenchmarkTwoTool import GroupTestBenchmarkTwoTool


class GroupTestBenchmarkThreeTool(GroupTestBenchmarkTwoTool):
    INFO_HIST_ELEMENT = "BM3 Info"
    REF_GSUITE_INPUT_LBL = 'Select a GSuite of case-control tracks with randomized labels'

    @classmethod
    def getExtraHistElements(cls, choices):
        """
        Defines extra history elements to be created when clicking execute.
        This is defined by a list of HistElement objects, as in the
        following example:

           from proto.GeneralGuiTool import HistElement
           return [HistElement(cls.HISTORY_TITLE, 'bed', hidden=False)]

        It is good practice to use class constants for longer strings.

        In the execute() method, one typically needs to fetch the path to
        the dataset referred to by the extra history element. To fetch the
        path, use the dict cls.extraGalaxyFn with the defined history title
        as key, e.g. "cls.extraGalaxyFn[cls.HISTORY_TITLE]".

        Optional method. Default return value if method is not defined: None
        """
        return [HistElement(cls.INFO_HIST_ELEMENT, "txt")]

    @classmethod
    def getToolName(cls):
        return "Group difference test - Benchmark three"

    # @staticmethod
    # def getOptionsBoxRandType(prevChoices):
    #     return '__hidden__', 'Between tracks'
    #
    # @staticmethod
    # def getOptionsBoxRandAlg(prevChoices):
    #     return '__hidden__', 'Shuffle whole tracks (for categorical gsuites)'


    @classmethod
    def _writeInfoBMLocal(cls, choices, results, fn):
        cls._writeInfo(3, choices, results, fn)
