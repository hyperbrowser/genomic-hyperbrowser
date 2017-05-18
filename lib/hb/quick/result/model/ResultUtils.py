from collections import OrderedDict


def getTrackTitleToResultDictFromFlatPairedTrackStructure(resultTrackStructure, titleTsKey="reference"):
    resDict = OrderedDict()
    for childTS in resultTrackStructure.values():
        assert childTS.isPairedTs(), "This method expects all second level nodes in the track structure to be of type PairedTS"
        resDict[childTS[titleTsKey].metadata['title']] = childTS.result
    return resDict
