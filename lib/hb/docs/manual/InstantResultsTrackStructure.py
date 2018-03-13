from InstantTrackStructure import orig
from gold.track.TSResult import TSResult


def fr1(orig):
    print 'Orig (fr1): ', orig
    rerooted = orig.makeTreeSegregatedByCategory(orig['r'])
    print 'Rerooted (fr1): ', rerooted
    tsresult = TSResult(rerooted)
    for category in rerooted:
        tsresult[category] = fr2(rerooted[category])
    return tsresult

def fr2(rerootedOneCategory):
    print 'Rerooted one cat (fr2): ', rerootedOneCategory
    pairwise = rerootedOneCategory['q'].makePairwiseCombinations(rerootedOneCategory['r'])
    print 'Pairwise one cat (fr2): ', pairwise
    tsresult = TSResult(pairwise)
    for keyname, pair in pairwise.items():
        tsresult[keyname] = fr3(pair)

    tsresult.setResult( '__'.join([childRes.getResult() for childRes in tsresult.values()]) )
    return tsresult

def fr3(pair):
    print 'Pair (fr3): ', pair
    resVal = '-'.join([sts.track.trackTitle for sts in pair.values()])
    return TSResult(pair, resVal)

print fr1(orig)['C1'].getResult()