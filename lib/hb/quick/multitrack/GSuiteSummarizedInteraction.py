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
from collections import OrderedDict
from gold.application.HBAPI import doAnalysis
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStat
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.track.Track import Track


class GSuiteSummarizedInteraction(object):
    '''
    classdocs
    '''

    def __init__(self, gsuite, analysisBins, rawStatistic, summaryFunc, reverse, randTrackClassTemplate=None ):
        '''
        Constructor
        '''
        self._gsuite = gsuite
        assert gsuite.numTracks() > 2, 'GSuite must contain more than 2 tracks.'
        self._analysisBins = analysisBins
        self._rawStatistic = rawStatistic
        self._summaryFunction = summaryFunc
        self._randTrackClassTemplate = randTrackClassTemplate
        self._reversed = reverse
        
    def run(self):
        tracks = [t.trackName for t in self._gsuite.allTracks()]
        trackTitles = self._gsuite.allTrackTitles()
        results = OrderedDict()
        analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksStat)
        analysisSpec.addParameter('rawStatistic', self._rawStatistic)
        analysisSpec.addParameter('summaryFunc', self._summaryFunction)
        analysisSpec.addParameter('reverse', self._reversed)
        for t1Title, t1 in zip(trackTitles, tracks):
            for t2Title, t2 in zip(trackTitles, tracks):
                if t1Title != t2Title:
                    result = doAnalysis(analysisSpec, self._analysisBins, [Track(t1), Track(t2)])
                    resultDict = result.getGlobalResult()
#                     if 'Result' in resultDict:
                    results[(t1Title, t2Title)] = resultDict['Result']
    