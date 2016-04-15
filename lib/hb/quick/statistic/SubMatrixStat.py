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
from quick.statistic.GraphMatrixStat import GraphMatrixStat
from gold.graph.GraphMatrix import GraphMatrix
from quick.statistic.PositionToGraphNodeIdStat import PositionToGraphNodeIdStat

class SubMatrixStat(MagicStatFactory):
    pass

class SubMatrixStatUnsplittable(Statistic):
    def _compute(self):
        #import pdb; pdb.set_trace()
        graphMatrix = self.matrix.getResult()
        ids = self.ids.getResult()
        #translate indices from IDs (such as 'chr1*100') to indices in array (such as '29')
        translated_indices = graphMatrix._translate(ids)
        subMatrix = graphMatrix.weights.take(translated_indices, axis=0)
        if subMatrix != []:
            subMatrix = subMatrix.take(translated_indices, axis=1)
        #wrap the new subMatrix in a GraphMatrix
        #TODO: is this a valid way to generate id -> position mapping?
        #assumes that the order in 'ids' is correct
        id2position = {id_name: row_num for row_num, id_name in enumerate(ids)}
        return GraphMatrix(weights=subMatrix, ids=id2position)

    def _createChildren(self):
        self.matrix = self._addChild(GraphMatrixStat(self._region, self._track))
        self.ids = self._addChild(PositionToGraphNodeIdStat(self._region, self._track, self._track2))
