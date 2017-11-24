from collections import OrderedDict


def dictifyTSResult(tsResult):
    resDict = OrderedDict()
    for k, v in tsResult.iteritems():
        resDict[k] = v.getResult()
    return resDict