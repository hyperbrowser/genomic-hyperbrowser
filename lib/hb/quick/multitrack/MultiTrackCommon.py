# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
# This file is part of The Genomic HyperBrowser.
#
#    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    The Genomic HyperBrowser is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
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

def getGSuiteDataFromGalaxyTN(galaxyTn):
    gSuite = getGSuiteFromGalaxyTN(galaxyTn)
    return getGSuiteDataFromGSuite(gSuite)

def getGSuiteFromGalaxyTN(galaxyTn):
    gSuiteFn = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
    return getGSuiteFromGSuiteFile(gSuiteFn)

def getGSuiteFromGSuiteFile(gSuiteFn):
    from gold.gsuite import GSuiteParser
    return GSuiteParser.parse(gSuiteFn)

def getGSuiteDataFromGSuiteFile(gSuiteFn):
    gSuite = getGSuiteFromGSuiteFile(gSuiteFn)
    return getGSuiteDataFromGSuite(gSuite)

def getSingleTrackGSuiteDataFromGalaxyTN(galaxyTn):
    titles, tracks, genome = getGSuiteDataFromGalaxyTN(galaxyTn)
    assert len(titles) > 0, 'GSuite must contain at least one track'
    return titles[0], tracks[0], genome
