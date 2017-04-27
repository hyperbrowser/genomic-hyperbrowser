from collections import OrderedDict


def getTrackTitleToResultDictFromTrackStructure(resultTrackStructure):
    resDict = OrderedDict()
    for childTS in resultTrackStructure.values():
        assert childTS.isPairedTs(), "This method expects all second level nodes in the track structure to be of type PairedTS"
        trackTitle = childTS['reference'].metadata['title']
        result = childTS.result
        resDict[trackTitle] = result

    return resDict
