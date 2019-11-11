import yaml

from gold.description.AnalysisDefHandler import YamlAnalysisDefHandler
from gold.track.TrackView import TrackView


def getKwArgOperationDictStat(analysisSpecsDict):
    opDict = {}
    kwDict = {}
    # for op, opCls in operations.items():
    #
    #     #opDict[op] = opCls.getKwArgumentInfoDict().keys()

    for statName,spec in analysisSpecsDict.iteritems():
        kwArgs = spec.getOptionsAsKeys().keys()
        # print 'op: ' + statName
        # print kwArgs
        opDict[statName] = kwArgs

    #print opDict

    for op, kwArgs in opDict.items():
        for kw in kwArgs:
            kwDict.setdefault(kw, []).append(op)

    return kwDict


def getYamlAnalysisSpecs(filePath):
    yamlAnalysisSpecList = []
    with open(filePath, 'r') as stream:
        analysisList = yaml.safe_load(stream)
        for analysis in analysisList:
            yamlAnalysisSpec = YamlAnalysisDefHandler(analysis)
            yamlAnalysisSpecList.append(yamlAnalysisSpec)

    return yamlAnalysisSpecList


def getAnalysisSpecsDict(analysisSpecList):
    specDict = {}
    for spec in analysisSpecList:
        if spec.getStatClass().__name__ == 'TrackOperationsManagerStat':
            name = spec.getChoice('rawStatistic')
            specDict[name] = spec
        else:
            specDict[spec.getStatClass().__name__] = spec

    return specDict


def parseBoolean(val):
    if type(val) == bool:
        return val
    if val == 'True':
        val = True
    elif val == 'False':
        val = False
    else:
        return None

    return val


def parseInt(val):
    if val:
        try:
            return int(val)
        except ValueError:
            return None

    return None


def createEmptyTrackView(tv):
    from numpy import array
    return TrackView(genomeAnchor=tv.genomeAnchor, startList=array([]),
                     endList=array([]), valList=None, strandList=None,
                     idList=None, edgesList=None, weightsList=None,
                     borderHandling=tv.borderHandling, allowOverlaps=False)