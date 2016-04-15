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

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from quick.statistic.GlobalGraphStat import GlobalGraphStat
from quick.statistic.NodeIdsInBinStat import NodeIdsInBinStat
from gold.util.CustomExceptions import SplittableStatNotAvailableError
from gold.util.CommonFunctions import isIter

class NeighborhoodOverlap3dStat(MagicStatFactory):
    pass

#class NeighborhoodOverlap3dStatSplittable():
#    pass

class NeighborhoodOverlap3dStatUnsplittable(Statistic):
    def _init(self, globalSource=None, weightThreshold=None, **kwArgs):
        if isIter(self._region):
            raise SplittableStatNotAvailableError()
        assert globalSource is not None
        assert weightThreshold is not None
        self._weightThreshold = float(weightThreshold)
        
    def _compute(self):
        globalGraph = self._globalGraphStat.getResult()
        nodeIds = self._nodeIdsInBinStat.getResult()
        if len(nodeIds)!=2: #currently, want to look at only pairwise correspondence
            return {'NumPossibleSharedNeighbors':None, \
                    'NumNodesInT1Neighborhood':None, \
                    'NumNodesInT2Neighborhood':None, \
                    'NumNodesOfNeighborOverlap':None, \
                    'ExpectedNumNodesOfNeighborOverlap':None, \
                    'NeighborOverlapEnrichment':None}#, 't1neighborhoodWeights':None}
        
        neighborhoods = [set([neighborEdge.toNode.id() for neighborEdge in globalGraph.getNode(nodeId).getNeighborIter() \
                              if (neighborEdge.weight is None or neighborEdge.weight>=self._weightThreshold) ]) for nodeId in nodeIds]

        #for nodeId, neighborhood in zip(nodeIds, neighborhoods):
        for neighborhood in neighborhoods:
            #assert not nodeId in neighborhood
            for nodeId in nodeIds:
                if nodeId in neighborhood:
                    neighborhood.remove(nodeId)
            
        numberOfPossibleSharedNeighbors = len(list(globalGraph.getNodeIter()))-2 #themselves can not be shared..

        neighborOverlap = len( neighborhoods[0].intersection(neighborhoods[1]) )
        expectedOverlap = (float(len(neighborhoods[0]))/numberOfPossibleSharedNeighbors ) * float(len(neighborhoods[1]))        
        neighborOverlapEnrichment = neighborOverlap/expectedOverlap if expectedOverlap>0 else None
        return {'NumPossibleSharedNeighbors':numberOfPossibleSharedNeighbors, \
                'NumNodesInT1Neighborhood':len( neighborhoods[0]), \
                'NumNodesInT2Neighborhood':len( neighborhoods[1]), \
                'NumNodesOfNeighborOverlap':neighborOverlap, \
                'ExpectedNumNodesOfNeighborOverlap':expectedOverlap, \
                'NeighborOverlapEnrichment':neighborOverlapEnrichment}#, 't1neighborhoodWeights':neighborhoodWeights[0]}
        #assert not graph.isDirected() ??
            
    def _createChildren(self):
        self._globalGraphStat = self._addChild(GlobalGraphStat(self._region, self._track, **self._kwArgs) )
        self._nodeIdsInBinStat = self._addChild(NodeIdsInBinStat(self._region, self._track))
