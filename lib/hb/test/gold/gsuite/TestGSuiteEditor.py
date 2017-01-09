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
from collections import OrderedDict

from gold.util.CustomExceptions import ArgumentValueError
import gold.gsuite.GSuiteEditor as GSuiteEditor
from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack

from test.gold.gsuite.GSuiteTestWithMockEncodingFuncs import GSuiteTestWithMockEncodingFuncs

class TestGSuiteEditor(GSuiteTestWithMockEncodingFuncs):

    # TODO: Test checks on location, fileFormat, trackType after adding tracks one at a time

    def setUp(self):
        GSuiteTestWithMockEncodingFuncs.setUp(self)

        self.track1 = GSuiteTrack('ftp://server.somewhere.com/path/to/file1.bed',
                                  title='Track1', genome='hg18',
                                  attributes=OrderedDict([('cell', 'k562'),
                                                          ('antibody', 'cMyb')]))

        self.track2 = GSuiteTrack('hb:/track/name/hierarchy',
                                  title='Track2', genome='hg18')

        self.track3 = GSuiteTrack('galaxy:/ad123dd12fg;btrack',
                                  title='Track3', genome='hg18',
                                  attributes=OrderedDict([('view', 'signal'),
                                                          ('antibody', 'cMyb')]))

    def testSelectRows(self):
        gSuite = GSuite(trackList=[self.track1, self.track2, self.track3])

        outGSuite = GSuiteEditor.selectRowsFromGSuiteByIndex(gSuite, [0,2])
        self.assertEquals([self.track1, self.track3], list(outGSuite.allTracks()))

        outGSuite = GSuiteEditor.selectRowsFromGSuiteByIndex(gSuite, [])
        self.assertEquals([], list(outGSuite.allTracks()))

        outGSuite = GSuiteEditor.selectRowsFromGSuiteByTitle(gSuite, ['Track1', 'Track3'])
        self.assertEquals([self.track1, self.track3], list(outGSuite.allTracks()))

        outGSuite = GSuiteEditor.selectRowsFromGSuiteByIndex(gSuite, [])
        self.assertEquals([], list(outGSuite.allTracks()))

        self.assertRaises(IndexError, GSuiteEditor.selectRowsFromGSuiteByIndex, gSuite, [3])
        self.assertRaises(KeyError, GSuiteEditor.selectRowsFromGSuiteByTitle, gSuite, ['Track4'])

    def testSelectAttributesEmpty(self):
        gSuite = GSuite(trackList=[self.track1, self.track2, self.track3])

        outGSuite = GSuiteEditor.selectColumnsFromGSuite(gSuite, selectedAttributes=[], selectTitle=False)
        self.assertEquals([], outGSuite.attributes)

        tracks = list(outGSuite.allTracks())
        self.assertEquals(OrderedDict(), tracks[0].attributes)
        self.assertEquals(OrderedDict(), tracks[1].attributes)
        self.assertEquals(OrderedDict(), tracks[2].attributes)

    def testSelectColumns(self):
        gSuite = GSuite(trackList=[self.track1, self.track2, self.track3])

        outGSuite = GSuiteEditor.selectColumnsFromGSuite(gSuite, selectedAttributes=['antibody', 'view'],
                                                         selectTitle=False)

        self.assertEquals(['antibody', 'view'], outGSuite.attributes)

        tracks = list(outGSuite.allTracks())

        self.assertEqual(tracks[0].uri, tracks[0].title)
        self.assertEqual(tracks[1].uri, tracks[1].title)
        self.assertEqual(tracks[2].uri, tracks[2].title)

        self.assertEquals(OrderedDict([('antibody', 'cMyb')]),
                          tracks[0].attributes)
        self.assertEquals(OrderedDict(),
                          tracks[1].attributes)
        self.assertEquals(OrderedDict([('antibody', 'cMyb'), ('view', 'signal')]),
                          tracks[2].attributes)

        self.assertRaises(KeyError, GSuiteEditor.selectColumnsFromGSuite, gSuite, ['something'])


if __name__ == "__main__":
    #TestGSuite().debug()
    unittest.main()
