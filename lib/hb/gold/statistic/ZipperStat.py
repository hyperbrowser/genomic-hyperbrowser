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

#UNTESTED
from gold.statistic.MagicStatFactory import MagicStatFactory
from gold.statistic.Statistic import Statistic
from gold.util.CustomExceptions import ShouldNotOccurError
from copy import copy

class ZipperStat(MagicStatFactory):
    pass

class ZipperStatUnsplittable(Statistic):
    IS_MEMOIZABLE = False
    
    def __init__(self, region, track, track2, statClassList=None, **kwArgs):
        Statistic.__init__(self, region, track, track2, statClassList=statClassList, **kwArgs)
        #self._kwArgs = kwArgs
        if type(statClassList) == list:
            self._statClassList = statClassList
        elif isinstance(statClassList, basestring):
            from gold.statistic.AllStatistics import STAT_CLASS_DICT
            self._statClassList = [STAT_CLASS_DICT[x] for x in \
                statClassList.replace(' ','').replace('^','|').split('|')]
        else:
            raise ShouldNotOccurError
    
    def _createChildren(self):
        kwArgs = copy(self._kwArgs)
        if 'statClassList' in kwArgs:
            del kwArgs['statClassList']
        for statClass in self._statClassList:
            self._addChild( statClass(self._region, self._track, (self._track2 if hasattr(self, '_track2') else None), **kwArgs) )
            
    def _compute(self):
        return [child.getResult() for child in self._children]
    
