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
from gold.description.AnalysisDefHandler import AnalysisSpec
from gold.gsuite import GSuiteComposer
from gold.gsuite.GSuite import GSuite
from gold.track.Track import Track
from gold.util import CommonConstants
from quick.statistic.GenericResultsCombinerStat import GenericResultsCombinerStat
from quick.statistic.NormalizedObservedVsExpectedStat import NormalizedObservedVsExpectedStat
from quick.statistic.PropOfReferenceTrackInsideTargetTrackStat import PropOfReferenceTrackInsideTargetTrackStat
from quick.statistic.PropOfReferenceTrackInsideUnionStat import PropOfReferenceTrackInsideUnionStat
from quick.statistic.RatioOfIntersectionToGeometricMeanStat import RatioOfIntersectionToGeometricMeanStat
from quick.statistic.RatioOfOverlapToUnionStat import RatioOfOverlapToUnionStat
from quick.statistic.StatFacades import ObservedVsExpectedStat
from quick.statistic.T1T2BinValuesCorrelationWithKendallCountStat import T1T2BinValuesCorrelationWithKendallCountStat


T1_RATIO_OF_SECOND_INSIDE_FIRST = 'Proportion of the query track base-pairs coinciding with base-pairs from the reference track'
T2_RATIO_OF_SECOND_INSIDE_UNION = 'Proportion of the union of base-pairs of the two tracks that are covered by the reference track'
T3_RATIO_OF_INTERSECTION_TO_UNION = 'Jaccard index: ratio of overlapping base-pairs relative to the union base-pairs'
T4_RATIO_OF_INTERSECTION_TO_GEOMETRIC_MEAN = 'Ratio of probability in being inside the intersection and the geometric mean of being inside each track'
T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP = 'Forbes coefficient: ratio of observed to expected overlap'
T6_STANDARD_DEVIATIONS_OF_OBSERVED_MINUS_EXPECTED_OVERLAP = 'Ratio of observed to expected overlap difference relative to the variance'
T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP = 'Normalized Forbes coefficient: ratio of observed to expected overlap normalized in relation to the reference GSuite'
T8_CORRELATED_BIN_COVERAGE = 'Correlated bin coverage'

PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING = OrderedDict([
                        (T5_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP, ObservedVsExpectedStat.__name__),
                        (T7_RATIO_OF_OBSERVED_TO_EXPECTED_OVERLAP, NormalizedObservedVsExpectedStat.__name__),
                        (T3_RATIO_OF_INTERSECTION_TO_UNION, RatioOfOverlapToUnionStat.__name__),
                        (T1_RATIO_OF_SECOND_INSIDE_FIRST, PropOfReferenceTrackInsideTargetTrackStat.__name__),
                        (T2_RATIO_OF_SECOND_INSIDE_UNION, PropOfReferenceTrackInsideUnionStat.__name__),
                        (T4_RATIO_OF_INTERSECTION_TO_GEOMETRIC_MEAN, RatioOfIntersectionToGeometricMeanStat.__name__),
                        # (T6_STANDARD_DEVIATIONS_OF_OBSERVED_MINUS_EXPECTED_OVERLAP, None),
                        (T8_CORRELATED_BIN_COVERAGE, T1T2BinValuesCorrelationWithKendallCountStat.__name__)
                                              ])
                                        
PAIRWISE_STAT_LABELS = PAIRWISE_STAT_LABEL_TO_CLASS_MAPPING.keys()

SUMMARY_FUNCTIONS_MAPPER = OrderedDict([('average', 'avg'), ('maximum', 'max'), ('minimum', 'min')])
SUMMARY_FUNCTIONS_LABELS = SUMMARY_FUNCTIONS_MAPPER.keys()

def runMultipleSingleValStatsOnTracks(gsuite, stats, analysisBins, queryTrack=None):
    '''
    gsuite: The gsuite of tracks
    stats: List of statistics
    analysisBins: BinSource object
    queryTrack: should be defined if there are stats that need to run on two tracks (e.g. overlap)
    
    Returns an OrderedDict: 
                    Track title -> OrderedDict: 
                                    Stat name -> single value'''
    
    assert stats is not None, 'stats argument not defined'
    assert type(stats) in [str, list], '''stats argument must be a list of statistics
                                         or ^-separated string of statistic names'''
    
    resultsDict = OrderedDict()
    additionalAnalysisSpec = AnalysisSpec(GenericResultsCombinerStat)
    
    statsParam = stats if isinstance(stats, basestring) else "^".join([x.__name__ for x in stats])
    
    additionalAnalysisSpec.addParameter('rawStatistics', statsParam) #use ^ separator to add additional stat classes.
    for refTrack in gsuite.allTracks():
        if refTrack.title not in resultsDict:
            resultsDict[refTrack.title] = OrderedDict()
        tracks = [Track(refTrack.trackName), queryTrack] if queryTrack else [Track(refTrack.trackName)]
        additionalResult = doAnalysis(additionalAnalysisSpec, 
                                      analysisBins, tracks).getGlobalResult()
        for statClassName, res in additionalResult.iteritems():
            statPrettyName = CommonConstants.STATISTIC_CLASS_NAME_TO_NATURAL_NAME_DICT[statClassName] if statClassName in CommonConstants.STATISTIC_CLASS_NAME_TO_NATURAL_NAME_DICT else statClassName
            resultsDict[refTrack.title][statPrettyName] = res

    return resultsDict


def addResultsToInputGSuite(gsuite, results, attrNames, outputGSuiteFN):
    '''
    Add the values from the analysis results as metadata columns and create a new GSuite.
    If the new attribute names in attrNames already exist as metadata columns in the GSuite,
    corresponding values will be overwritten.
    '''
    assert isinstance(attrNames, (list, tuple)), 'attrNames must be of type list or tuple: %s' % str(attrNames)
    outGSuite = GSuite()
    for gsTrack in gsuite.allTracks():
        currentTrackRes = results[gsTrack.title]
        if len(attrNames) == 1:
            if isinstance(currentTrackRes, (list, tuple)):
                if currentTrackRes[0]:
                    gsTrack.setAttribute(attrNames[0], str(currentTrackRes[0]))
            else:
                if currentTrackRes:
                    gsTrack.setAttribute(attrNames[0], str(currentTrackRes))
        else:
            assert isinstance(currentTrackRes, (list, tuple)), 'Expected multiple results per track. Attribute names %s' % str(attrNames)
            for i, resultVal in enumerate(currentTrackRes):
                if resultVal:
                    gsTrack.setAttribute(attrNames[i], str(resultVal))
        outGSuite.addTrack(gsTrack)
    GSuiteComposer.composeToFile(outGSuite, outputGSuiteFN)
