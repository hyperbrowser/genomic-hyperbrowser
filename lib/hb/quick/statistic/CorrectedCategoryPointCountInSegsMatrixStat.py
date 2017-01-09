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
from gold.statistic.Statistic import Statistic, OnlyGloballySplittable, StatisticNumpyMatrixSplittable
from gold.statistic.CategoryPointCountInSegsMatrixStat import CategoryPointCountInSegsMatrixStat
from copy import copy
from collections import OrderedDict
import numpy

class CorrectedCategoryPointCountInSegsMatrixStat(MagicStatFactory):
    pass

class CorrectedCategoryPointCountInSegsMatrixStatSplittable(StatisticNumpyMatrixSplittable, OnlyGloballySplittable):
    pass
            
class CorrectedCategoryPointCountInSegsMatrixStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, maxCountRegionSize='None', **kwArgs):
        if maxCountRegionSize == 'None':
            self._maxCountRegionSize = None
        else:
            self._maxCountRegionSize = int(maxCountRegionSize)
        Statistic.__init__(self, region, track, track2, maxCountRegionSize=maxCountRegionSize, **kwArgs)
        
    def _compute(self):
        resDict = self._children[0].getResult().get('Result')
        assert resDict is not None
                                                    
        matrix = resDict.get('Matrix')
        assert matrix is not None

        if not self._maxCountRegionSize is None:
            #Divides the counts of large bins by the (integer) ratio between the bin size and a specified maximal region size
            matrix = numpy.array(matrix/((len(self._region)/self._maxCountRegionSize)+1), dtype = 'int32')
        
        return {'Result': OrderedDict([('Matrix', matrix), ('Rows', resDict.get('Rows')), ('Cols', resDict.get('Cols'))])}

    
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        del kwArgs['maxCountRegionSize']
        self._addChild(CategoryPointCountInSegsMatrixStat(self._region, self._track, self._track2, **kwArgs))

