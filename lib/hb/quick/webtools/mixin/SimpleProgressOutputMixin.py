class SimpleProgressOutputMixin(object):

    @classmethod
    def _calculateNrOfOperationsForProgresOutput(cls, ts, analysisBins, choices, isMC=True,
                                                 runLocalAnalysis=False):
        from gold.description.AnalysisDefHandler import AnalysisDefHandler
        from gold.description.AnalysisList import REPLACE_TEMPLATES
        n = len(ts.getQueryTS().getLeafNodes())
        m = len(ts.getReferenceTS().getLeafNodes())
        k = len(list(analysisBins)) + 1 if runLocalAnalysis else 1
        maxSamples = 0
        if isMC:
            mcfdrDepth = choices.mcfdrDepth if choices.mcfdrDepth else \
                AnalysisDefHandler(REPLACE_TEMPLATES['$MCFDRv5$']).getOptionsAsText().values()[0][0]
            analysisDefString = REPLACE_TEMPLATES['$MCFDRv5$'] + ' -> ' + ' -> MultipleRandomizationManagerStat'
            analysisSpec = AnalysisDefHandler(analysisDefString)
            analysisSpec.setChoice('MCFDR sampling depth', mcfdrDepth)
            analysisDef = AnalysisDefHandler(analysisSpec.getDefAfterChoices())
            aDChoicec = analysisDef.getChoices(filterByActivation=True)
            maxSamples = int(aDChoicec['maxSamples'])
        return n * m * k * (maxSamples + 1)


    @classmethod
    def _endProgressOutput(cls):
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.divEnd()
        core.hideToggle(styleId="progress-output")
        print str(core)

    @classmethod
    def _startProgressOutput(cls):
        from proto.hyperbrowser.HtmlCore import HtmlCore
        core = HtmlCore()
        core.begin()
        core.divBegin(divId="progress-output")
        print str(core)
