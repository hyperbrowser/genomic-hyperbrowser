from gold.track.trackstructure.TsVisitors import TsSwapOrigWithRandomTracksVisitor, \
    TsTreeWriterVisitor


def getRandomizedVersionOfTs(trackStructure, randTvProvider, randIndex=0):
    visitor = TsSwapOrigWithRandomTracksVisitor()
    newTs = visitor.visitAllNodesAndReturnModifiedCopyOfTS(trackStructure, randTvProvider,
                                                           randIndex=randIndex)
    return newTs


def getTsTreeStructureAsStr(trackStructure):
    visitor = TsTreeWriterVisitor()
    return visitor.visitAllNodesWithLevelAndKeyArg(trackStructure, level=0, key=None)
