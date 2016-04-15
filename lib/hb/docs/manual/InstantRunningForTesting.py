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

#WORKING AS OF April 5, 2015

from gold.application.HBAPI import doAnalysis, GlobalBinSource, AnalysisSpec
#from gold.application.HBAPI import RegionIter, AnalysisDefHandler, GenomeRegion
from gold.track.Track import Track
from quick.statistic.SummarizedInteractionWithOtherTracksStat import SummarizedInteractionWithOtherTracksStat
from collections import OrderedDict
from quick.statistic.CollectionVsCollectionStat import CollectionVsCollectionStat
from quick.statistic.StatFacades import TpRawOverlapStat
from quick.statistic.QueryToReferenceCollectionWrapperStat import QueryToReferenceCollectionWrapperStat

analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksStat)
analysisSpec.addParameter("withOverlaps","yes")

analysisBins = GlobalBinSource('hg18')
tracks = [ 
          Track(['Genes and gene subsets','Genes','Refseq']),
          Track(['Genes and gene subsets','Genes','CCDS']),
          Track(['Genes and gene subsets','Genes','Ensembl']),
          Track(['Genes and gene subsets','Genes','GeneID'])
          
           ]
trackTitles = ['refseq', 'CCDS', 'Ensembl', 'GeneID']
# results = OrderedDict()
# analysisSpec = AnalysisSpec(SummarizedInteractionWithOtherTracksStat)
# analysisSpec = AnalysisSpec(CollectionVsCollectionStat)
analysisSpec = AnalysisSpec(QueryToReferenceCollectionWrapperStat)
# analysisSpec.addParameter('rawStatistic', 'RatioOfOverlapToUnionStat')
# analysisSpec.addParameter('rawStatistic', 'TpRawOverlapStat')
analysisSpec.addParameter('pairwiseStat', 'RatioOfOverlapToUnionStat')
# analysisSpec.addParameter('summaryFunc', 'avg')
# analysisSpec.addParameter('reverse', 'No')
# analysisSpec.addParameter('firstCollectionTrackNr', '2')
results = doAnalysis(analysisSpec, analysisBins, tracks)
# print results
# for t1Title, t1 in zip(trackTitles, tracks):
#     for t2Title, t2 in zip(trackTitles, tracks):
#         if t1Title != t2Title:
#             result = doAnalysis(analysisSpec, analysisBins, [t1, t2])
#             resultDict = result.getGlobalResult()
# #                     if 'Result' in resultDict:
#             results[(t1Title, t2Title)] = resultDict['Result']
# for key,val in results.iteritems():
#     print key
#     print val
#     print '____________________'