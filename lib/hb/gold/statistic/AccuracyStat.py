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

import math
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.statistic.RawOverlapStat import RawOverlapStat
from gold.statistic.DerivedOverlapStat import DerivedOverlapStat

class AccuracyStat(MagicStatFactory):
    pass

class AccuracyStatUnsplittable(Statistic):
    def __init__(self, region, track, track2, **kwArgs):
        Statistic.__init__(self, region, track, track2, **kwArgs)

    def _createChildren(self):
        self._addChild( RawOverlapStat(self._region, self._track, self._track2) )
        self._addChild( DerivedOverlapStat(self._region, self._track, self._track2) )
        
    def _compute(self):
        accus = {}
        accus["recall"] = self._children[1].getResult()["1inside2"]
        accus["precision"] = self._children[1].getResult()["2inside1"]
        #tp = self._children[0].getResult()["TP"]
        #tn = self._children[0].getResult()["TN"]
        #fp = self._children[0].getResult()["FP"]
        #fn = self._children[0].getResult()["FN"]
        tn,fp,fn,tp = [ float(self._children[0].getResult()[key]) for key in ['Neither','Only1','Only2','Both'] ]
        
        #tp,tn,fp,fn = [float(x) for x in [tp,tn,fp,fn]]
        
        if 0 in [ (tp + fp) , (tn + fn) , (tp + fn) , (tn + fp)]:
            accus["cc"] = None
        else:
            accus["cc"]= ((tp * tn) - (fp * fn) ) / (math.sqrt(tp + fp)*math.sqrt(tn + fn)*math.sqrt(tp + fn)*math.sqrt(tn + fp))
        accus["hammingDistance"] = fp + fn
        
        return accus


