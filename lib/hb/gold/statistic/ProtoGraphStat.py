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

import ast

from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic, StatisticSplittable
from gold.track.TrackFormat import TrackFormatReq
from gold.graph.GraphView import LazyProtoGraphView
from gold.statistic.RawDataStat import RawDataStat
from gold.description.TrackInfo import TrackInfo

class ProtoGraphStat(MagicStatFactory):
    pass

class ProtoGraphStatSplittable(StatisticSplittable):
    IS_MEMOIZABLE = False

    def _combineResults(self):
        self._result = LazyProtoGraphView.mergeProtoGraphViews(self._childResults)
        
class ProtoGraphStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def _init(self, isDirected='fromTrack', **kwArgs):
        assert isDirected in ['fromTrack','True','False']
        self._forceIsDirected = isDirected != 'fromTrack'
        self._isDirected = ast.literal_eval(isDirected) if self._forceIsDirected else None

    def _compute(self):
        tv = self._children[0].getResult()
        
        if not self._forceIsDirected:
            from gold.track.RandomizedTrack import RandomizedTrack
            origTrackName = self._track.trackName[:-2] if isinstance(self._track, RandomizedTrack) else self._track.trackName
            isDirected = not (TrackInfo(self._region.genome, origTrackName).undirectedEdges == True)
        else:
            isDirected = self._isDirected
        
        return LazyProtoGraphView.createInstanceFromTrackView(tv, isDirected=isDirected)
    
    def _createChildren(self):
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(linked=True, allowOverlaps=False), **self._kwArgs) )
