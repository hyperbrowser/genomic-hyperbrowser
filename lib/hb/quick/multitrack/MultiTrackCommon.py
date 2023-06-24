try:
    from functools import lru_cache
except ImportError:
    from backports.functools_lru_cache import lru_cache

from quick.application.ExternalTrackManager import ExternalTrackManager
'''
Created on Nov 21, 2014

@author: boris
'''


def getGSuiteDataFromGSuite(gSuite):
    assert gSuite.isPreprocessed(), 'GSuite file contains tracks that are not preprocessed'
    genome = gSuite.genome
    trackTitles = gSuite.allTrackTitles()
    internalTracks = [track.trackName for track in gSuite.allTracks()]
    return trackTitles, internalTracks, genome

@lru_cache()
def getGSuiteDataFromGalaxyTN(galaxyTn):
    gSuite = getGSuiteFromGalaxyTN(galaxyTn)
    return getGSuiteDataFromGSuite(gSuite)

@lru_cache()
def getGSuiteFromGalaxyTN(galaxyTn):
    gSuiteFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
    return getGSuiteFromGSuiteFile(gSuiteFn)

@lru_cache()
def getGSuiteFromGSuiteFile(gSuiteFn):
    from gold.gsuite import GSuiteParser
    return GSuiteParser.parse(gSuiteFn)

@lru_cache()
def getGSuiteDataFromGSuiteFile(gSuiteFn):
    gSuite = getGSuiteFromGSuiteFile(gSuiteFn)
    return getGSuiteDataFromGSuite(gSuite)

@lru_cache()
def getSingleTrackGSuiteDataFromGalaxyTN(galaxyTn):
    titles, tracks, genome = getGSuiteDataFromGalaxyTN(galaxyTn)
    assert len(titles) > 0, 'GSuite must contain at least one track'
    return titles[0], tracks[0], genome
