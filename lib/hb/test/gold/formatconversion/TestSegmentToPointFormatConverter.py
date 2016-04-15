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

import unittest
#from gold.formatconversion.FormatConverter import getFormatConverter
from gold.formatconversion.SegmentToPointFormatConverter import SegmentToPointFormatConverter, \
    SegmentToStartPointFormatConverter, SegmentToMidPointFormatConverter, SegmentToEndPointFormatConverter
from gold.track.TrackView import TrackView
from gold.track.TrackFormat import TrackFormatReq
from test.gold.track.common.SampleTrackView import SampleTV

class TestFormatConverter(unittest.TestCase):
    def setUp(self):
        pass
    
    def _assertConvertSegmentToPoint(self, targetStarts, sourceTv, converterCls):
        pointFormat = TrackFormatReq(interval=False, dense=False)
        self.assertTrue(converterCls.canHandle(sourceTv.trackFormat, pointFormat))
 
        targetTv = converterCls.convert(sourceTv)
        self.assertTrue(pointFormat.isCompatibleWith(targetTv.trackFormat))
            
        self.assertEqual(targetStarts, [el.start() for el in targetTv])
        for el in targetTv:
            self.assertEqual(el.start() + 1, el.end())
            
    def testConvertSegmentToPoint(self):
        segSourceTv = SampleTV(segments=[[2,6], [10,20]], strands=[True,False])
        self._assertConvertSegmentToPoint([2,19], segSourceTv, SegmentToStartPointFormatConverter)
        self._assertConvertSegmentToPoint([4,15], segSourceTv, SegmentToMidPointFormatConverter)
        self._assertConvertSegmentToPoint([5,10], segSourceTv, SegmentToEndPointFormatConverter)
        
        #partSourceTv = SampleTV(ends=[5,11], strands=False, anchor=[0,11])
        #self._assertConvertSegmentToPoint([0,5], partSourceTv, SegmentToStartPointFormatConverter)
        #self._assertConvertSegmentToPoint([2,8], partSourceTv, SegmentToMidPointFormatConverter)
        #self._assertConvertSegmentToPoint([4,10], partSourceTv, SegmentToEndPointFormatConverter)

        segSourceTv = SampleTV(segments=[], strands=False)
        self._assertConvertSegmentToPoint([], segSourceTv, SegmentToStartPointFormatConverter)
        
    def testConvertSegmentToPointWithOverlaps(self):
        segSourceTv = SampleTV(segments=[[2,20], [7,11]], strands=False, allowOverlaps=True)
        self._assertConvertSegmentToPoint([2,7], segSourceTv, SegmentToStartPointFormatConverter)
        self._assertConvertSegmentToPoint([9,11], segSourceTv, SegmentToMidPointFormatConverter)
        self._assertConvertSegmentToPoint([10,19], segSourceTv, SegmentToEndPointFormatConverter)

        segSourceTv = SampleTV(segments=[], strands=False, allowOverlaps=True)
        self._assertConvertSegmentToPoint([], segSourceTv, SegmentToStartPointFormatConverter)

    def _assertFailedConversion(self, sourceTv, tfReq):
        self.assertFalse(SegmentToStartPointFormatConverter.canHandle(sourceTv.trackFormat, tfReq))
 
    def testConvertSegmentToPointReqFails(self):
        segSourceTv = SampleTV(segments=[[2,20], [7,11]]) 
        self._assertFailedConversion(segSourceTv, \
                                     TrackFormatReq(interval=False, dense=False, val='category'))
        self._assertFailedConversion(segSourceTv, \
                                     TrackFormatReq(interval=False, dense=False, strand=True))
    
if __name__ == "__main__":
    unittest.main()
    
        #FormatConverter = getFormatConverter(sourceTv.trackFormat, pointFormat)
        #self.assertTrue('SegmentToPointFormatConverter', FormatConverter.__class__.__name__)
