from collections import OrderedDict


def getTrackTitleToResultDictFromFlatPairedTrackStructure(resultTrackStructure):
    resDict = OrderedDict()
    for childTS in resultTrackStructure.values():
        assert childTS.isPairedTs(), "This method expects all second level nodes in the track structure to be of type PairedTS"
        resDict[childTS['reference'].metadata['title']] = childTS.result
    return resDict
