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
from gold.statistic.GraphStat import GraphStat
from gold.graph.GraphMatrix import GraphMatrix
import numpy as np

class GraphMatrixStat(MagicStatFactory):
    pass

class GraphMatrixStatUnsplittable(Statistic):
    def _compute(self):
        #version 1: using the iterator based implementation for generating matrices
        #instance of GraphMatrix class:
        res = self._graphStat.getResult().getEdgeWeightMatrixRepresentation(completeMatrix=False, rowsAsFromNodes=True, missingEdgeWeight=np.nan)
        assert (res['Rows'] == res['Cols']).all() #rows and column IDs should be the same
        #TODO: the way ids are created is based on assumptions that may not hold:
        graphMatrix = GraphMatrix(weights=res['Matrix'], ids={i: n for n, i in enumerate(res['Rows'])})
        return graphMatrix

        #version 2: using optimized method that assumes complete graphs:
        #res = self._graphStat.getResult().getMatrixAndIdsFromCompleteGraph()
        #graphMatrix = GraphMatrix(weights=res["matrix"], ids=res["ids"])
        #return graphMatrix

    def _createChildren(self):
        self._graphStat = self._addChild(GraphStat(self._region, self._track))
