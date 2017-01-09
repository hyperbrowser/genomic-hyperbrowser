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
from quick.statistic.RawCaseVsControlOverlapDifferenceStat import RawCaseVsControlOverlapDifferenceStat

class DerivedCaseVsControlOverlapDifferenceStat(MagicStatFactory):
    pass

class DerivedCaseVsControlOverlapDifferenceStatUnsplittable(Statistic):
    #from gold.util.CommonFunctions import repackageException
    #from gold.util.CustomExceptions import ShouldNotOccurError
    #@repackageException(Exception, ShouldNotOccurError)            
    def _compute(self): #Numpy Version..
        res = self._children[0].getResult()
        tnCase,fpCase,fnCase,tpCase,tnControl,fpControl,fnControl,tpControl = [res[x] for x in 'tnCase,fpCase,fnCase,tpCase,tnControl,fpControl,fnControl,tpControl'.split(',')]
        
        controlBpOverlap = tpControl
        controlPropOverlapping = 1.0*tpControl/(tpControl+fpControl) if (tpControl+fpControl)>0 else None
        caseBpOverlap =tpCase
        casePropOverlapping = 1.0*tpCase/(tpCase+fpCase) if (tpCase+fpCase)>0 else None
        caseVsControlPropRatio = (casePropOverlapping / controlPropOverlapping) if controlPropOverlapping>0 else None

        return dict(zip('caseBpOverlap,controlBpOverlap,casePropOverlapping,controlPropOverlapping,caseVsControlPropRatio'.split(','), \
                [caseBpOverlap,controlBpOverlap,casePropOverlapping, controlPropOverlapping, caseVsControlPropRatio]))

        
    def _createChildren(self):
        self._addChild(RawCaseVsControlOverlapDifferenceStat(self._region, self._track, self._track2 ))
