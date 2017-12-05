from collections import OrderedDict

from quick.util.CommonFunctions import smartDiff, smartMeanWithNones, minAndMax, minLqMedUqMax

FUNCTION_DICT = OrderedDict([('diff', smartDiff),
                             ('avg', smartMeanWithNones),
                             ('max', max),
                             ('min', min),
                             ('minAndMax', minAndMax),
                             ('raw', 'RawResults'),
                             ('minLqMedUqMax', minLqMedUqMax)])


def getSummaryFunctionDict():
    import copy
    return copy.copy(FUNCTION_DICT)

def getFilteredSummaryFunctionDict(keys):
    assert isinstance(keys, list)
    retDict = OrderedDict()
    for key, val in getSummaryFunctionDict().items():
        if key in keys:
            retDict[key] = val
    return retDict

def resolveSummaryFunctionFromLabel(summaryFunc, functionDict):
    from gold.util.CustomExceptions import ShouldNotOccurError
    if summaryFunc not in functionDict:
        raise ShouldNotOccurError(str(summaryFunc) +
                                  ' is not in the list of allowed summary functions, must be one of ' +
                                  str(sorted(functionDict.keys())))
    else:
        return functionDict[summaryFunc]
