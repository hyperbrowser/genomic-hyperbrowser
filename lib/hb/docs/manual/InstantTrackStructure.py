#TO DISCUSS
#Redundant that key is typically just title of underlying TS. Could have method addChild, which takes a TS and accesses its title and uses this as key to put in as a key-value mapping in itself?!
#TS should probably have a str method?
#What is the best definition of equals of TrackStructure, as used in _copySegregatedSubtree?
#What could/should TSResult assert in __setitem__ - this depends on what TSs we want the RTS to refer to..
from collections import OrderedDict

from gold.track.Track import Track
from gold.track.TrackStructure import FlatTracksTS, SingleTrackTS, TrackStructureV2

class MockTrack(Track):
    def __new__(cls,*args):
        return object.__new__(cls)

    def __init__(self,name):
        object.__init__(self)
        self.trackName = [name] #because needed by hash in makeTreeSegregatedByCategory
        self.trackTitle = name

q = SingleTrackTS( MockTrack('t1'), OrderedDict(title='t1', cat='q') )

flat = FlatTracksTS()
flat['t2'] = SingleTrackTS( MockTrack('t2'), OrderedDict(title='t2', cat='C1') )
flat['t3'] = SingleTrackTS( MockTrack('t3'), OrderedDict(title='t3', cat='C1') )
flat['t4'] = SingleTrackTS( MockTrack('t4'), OrderedDict(title='t4', cat='C2') )

r = flat.getSplittedByCategoryTS('cat')

orig = TrackStructureV2()
orig['q'] = q
orig['r'] = r

def allInOne():
    print 'Orig: ', orig
    rerooted = orig.makeTreeSegregatedByCategory(orig['r'])
    print 'Rerooted: ', rerooted

    c1Pairwise = rerooted['C1']['q'].makePairwiseCombinations(rerooted['C1']['r'])
    print 'c1Pairwise: ', c1Pairwise

def f1(orig):
    print 'Orig (f1): ', orig
    rerooted = orig.makeTreeSegregatedByCategory(orig['r'])
    print 'Rerooted (f1): ', rerooted
    for category in rerooted:
        f2(rerooted[category])

def f2(rerootedOneCategory):
    print 'Rerooted one cat (f2): ', rerootedOneCategory
    pairwise = rerootedOneCategory['q'].makePairwiseCombinations(rerootedOneCategory['r'])
    print 'Pairwise one cat (f2): ', pairwise
    for pair in pairwise.values():
        f3(pair)

def f3(pair):
    print 'Pair (f3): ', pair

allInOne()
#f1(orig)
