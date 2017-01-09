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

# NB: TrackFormat == TrackFormat is not tested

import unittest
from gold.graph.NodeElement import NodeElement
from test.gold.track.common.SampleTrackView import SampleTV

class TestNodeElement(unittest.TestCase):
    def setUp(self):
        pass

    def testNeighborTraversing(self):
        tv = SampleTV(starts=[1,2,3,5], ids=list('1234'), edges=[list('23'), list('14'), list('1'), list('2')])
        raise Exception   
        #graphView = 
        n = NodeElement(tv, 0, graphView)
        #e = Edge()
    
if __name__ == "__main__":
    unittest.main()
