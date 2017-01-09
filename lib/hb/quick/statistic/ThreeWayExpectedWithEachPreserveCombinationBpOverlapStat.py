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
#from gold.statistic.RawDataStat import RawDataStat
#from gold.track.TrackFormat import TrackFormatReq
from quick.statistic.ThreeWayProportionalBpOverlapStat import ThreeWayProportionalBpOverlapStat
#from quick.statistic.ThreeWayBpOverlapProportionalToGlobalBpsStat import ThreeWayBpOverlapProportionalToGlobalBpsStat

class ThreeWayExpectedWithEachPreserveCombinationBpOverlapStat(MagicStatFactory):
    pass

            
class ThreeWayExpectedWithEachPreserveCombinationBpOverlapStatUnsplittable(Statistic):
    def _compute(self):        
        t = self._children[0].getResult()
        numTracks = len(t.keys()[0]) #due to binary coding of track combinations
        if numTracks != 3:
            return None
        
        a,b,c = t['100'], t['010'], t['001']
        ab, ac, bc = t['110'], t['101'], t['011']
        abc = t['111']
        cGivenA = ac/a
        cGivenB = bc/b
        
        res = {}
        res['preserveNone'] = a*b*c
        res['preserveAB'] = ab*c
        res['preserveAC'] = ac*b
        res['preserveBC'] = bc*a
        res['preserveAB_AC'] = ab*cGivenA
        res['preserveAB_BC'] = ab*cGivenB
        res['preserveAC_BC'] = ac*cGivenB
        res['preserveAll'] = abc
        
        return res
                        
    def _createChildren(self):
        self._addChild( ThreeWayProportionalBpOverlapStat(self._region, self._track, self._track2, **self._kwArgs) )