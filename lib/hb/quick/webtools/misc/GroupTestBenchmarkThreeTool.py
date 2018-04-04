from quick.webtools.misc.GroupTestBenchmarkTwoTool import GroupTestBenchmarkTwoTool


class GroupTestBenchmarkThreeTool(GroupTestBenchmarkTwoTool):
    @classmethod
    def getToolName(cls):
        return "Group difference test - Benchmark three"

    @staticmethod
    def getOptionsBoxRandType(prevChoices):
        return '__hidden__', 'Between tracks'

    @staticmethod
    def getOptionsBoxRandAlg(prevChoices):
        return '__hidden__', 'Shuffle whole tracks (for categorical gsuites)'
