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
from gold.statistic.RawDataStat import RawDataStat
from gold.track.TrackFormat import TrackFormatReq
from gold.util.CustomExceptions import ShouldNotOccurError

class BpLevelArrayRawDataStat(MagicStatFactory):
    pass

class BpLevelArrayRawDataStatUnsplittable(Statistic):
    def _init(self, bpDepthType='coverage', useFloatValues=False, **kwArgs):

        assert bpDepthType in ['coverage','binary']
        self._bpDepthType = bpDepthType

        assert useFloatValues in [True, 'True', False,'False']
        self._useFloatValues = useFloatValues in [True, 'True']

    def _compute(self): #Numpy Version..
        tv = self._children[0].getResult()

        if self._bpDepthType == 'coverage':
            vals = tv.getCoverageBpLevelArray()
        elif self._bpDepthType == 'binary':
            vals = tv.getBinaryBpLevelArray()
        else:
            raise ShouldNotOccurError

        if self._useFloatValues:
            return vals.astype('float64')

        else:
            return vals


    def _createChildren(self):
        allowOverlaps = self._configuredToAllowOverlaps(strict=False, allowReturningNone=True)
        self._addChild( RawDataStat(self._region, self._track, TrackFormatReq(allowOverlaps=allowOverlaps)) )

    def _afterComputeCleanup(self):
        if self.hasResult():
            del self._result
