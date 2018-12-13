import unittest
from collections import OrderedDict

import config.Config
config.Config.ALLOW_GSUITE_FILE_PROTOCOL = True

from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
from gold.util.CustomExceptions import InvalidFormatError, ArgumentValueError

from test.gold.gsuite.GSuiteTestWithMockEncodingFuncs import GSuiteTestWithMockEncodingFuncs


class TestGSuite(GSuiteTestWithMockEncodingFuncs):
    def testEmptyGSuite(self):
        gSuite = GSuite()

        self.assertEqual('unknown', gSuite.location)
        self.assertEqual('unknown', gSuite.fileFormat)
        self.assertEqual('unknown', gSuite.trackType)
        self.assertEqual('unknown', gSuite.genome)
        self.assertEqual(OrderedDict(), gSuite.customHeaders)
        self.assertEqual([], gSuite.attributes)

        self.assertEqual(False, gSuite.isPreprocessed())
        self.assertEqual(False, gSuite.hasCustomTitles())

        self.assertEqual(0, gSuite.numTracks())
        self.assertEqual(0, len(list(gSuite.allTracks())))
        self.assertEqual(0, len(list(gSuite.allTrackTitles())))
        self.assertEqual(0, len(list(gSuite.allTrackTypes())))

    def testCustomHeaders(self):
        gSuite = GSuite(customHeaders=OrderedDict([('My Header', 'My value')]))
        self.assertEqual(OrderedDict([('my header', 'My value')]), gSuite.customHeaders)
        self.assertEqual('My value', gSuite.getCustomHeader('my header'))
        self.assertEqual(None, gSuite.getCustomHeader('wrong header'))

        gSuite.customHeaders = OrderedDict([('My New Header', 'My new value')])
        gSuite.setCustomHeader('my_second_header', 'My other value')
        self.assertEqual('My other value', gSuite.getCustomHeader('my_second_header'))
        self.assertEqual(['my new header', 'my_second_header'], gSuite.customHeaders.keys())
        self.assertEqual(['My new value', 'My other value'], gSuite.customHeaders.values())

        with self.assertRaises(AttributeError):
            gSuite.my_new_header
        self.assertEqual('My other value', gSuite.my_second_header)

        with self.assertRaises(ArgumentValueError):
            gSuite.customHeaders = OrderedDict([('a', 'value'), ('A', 'other value')])

    def testAddGSuiteTracks(self):
        gSuite = GSuite()
        gSuite.setGenomeOfAllTracks('hg18')

        self.assertEqual('unknown', gSuite.genome)

        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/path/to/file1.bed',
                                    title='Track1',
                                    attributes=OrderedDict([('cell', 'k562'),
                                                            ('antibody', 'cMyb')])))
        gSuite.addTrack(GSuiteTrack('http://server.other.com/path/to/file2.bed',
                                    title='Track2',
                                    attributes=OrderedDict([('cell', 'GM12878'),
                                                            ('antibody', 'cMyc')])))
        gSuite.addTrack(GSuiteTrack('https://server.other.com/path/to/file3.bed',
                                    attributes=OrderedDict([('cell', 'GM12878'),
                                                            ('antibody', 'cMyb')])))
        gSuite.addTrack(GSuiteTrack('rsync://server.other.com/other/path/to/file3.bed;bed9',
                                    attributes=OrderedDict([('cell', 'NHFL')])))
        gSuite.setGenomeOfAllTracks('hg18')

        self.assertEqual('remote', gSuite.location)
        self.assertEqual('primary', gSuite.fileFormat)
        self.assertEqual('unknown', gSuite.trackType)
        self.assertEqual('hg18', gSuite.genome)
        self.assertEqual(['cell', 'antibody'], gSuite.attributes)

        self.assertEqual(False, gSuite.isPreprocessed())
        self.assertEqual(True, gSuite.hasCustomTitles())

        self.assertEqual(4, gSuite.numTracks())
        self.assertEqual(['hg18'] * 4, [x.genome for x in gSuite.allTracks()])
        self.assertEqual(['Track1', 'Track2', 'file3.bed', 'file3.bed (2)'],
                         gSuite.allTrackTitles())
        self.assertEqual(['unknown'], gSuite.allTrackTypes())

        gSuite.addTrack(GSuiteTrack('hb:/track/name/hierarchy',
                                    title='Track1', genome='hg19', trackType='segments'))
        self.assertEqual('multiple', gSuite.genome)

        gSuite.addTrack(GSuiteTrack('galaxy:/ad123dd12fg;btrack?track=track:name',
                                    title='Track2',
                                    attributes=OrderedDict([('cell', 'k562'),
                                                            ('antibody', 'cMyb')])))
        gSuite.addTrack(GSuiteTrack('file:/path/to/file.btrack?track=track:name',
                                    title='Track2',
                                    attributes=OrderedDict([('antibody', 'cMyb'),
                                                            ('extra', 'yes')])))

        self.assertEqual('multiple', gSuite.location)
        self.assertEqual('multiple', gSuite.fileFormat)
        self.assertEqual('unknown', gSuite.trackType)
        self.assertEqual('unknown', gSuite.genome)
        self.assertEqual(['cell', 'antibody', 'extra'], gSuite.attributes)

        self.assertEqual(False, gSuite.isPreprocessed())
        self.assertEqual(True, gSuite.hasCustomTitles())

        self.assertEqual(7, gSuite.numTracks())
        self.assertEqual(['hg18'] * 4 + ['hg19'] + ['unknown'] * 2,
                         [x.genome for x in gSuite.allTracks()])
        self.assertEqual(['Track1', 'Track2', 'file3.bed', 'file3.bed (2)',
                          'Track1 (2)', 'Track2 (2)', 'Track2 (3)'],
                         gSuite.allTrackTitles())
        self.assertEqual(['segments', 'unknown'],
                         gSuite.allTrackTypes())

        self.assertRaises(InvalidFormatError, gSuite.addTrack,
                          GSuiteTrack('https://server.third.com/path/to/file3.bed'),
                          allowDuplicateTitles=False)

    def testSimpleTitleDuplicate(self):
        gSuite = GSuite()
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/path/to/file1.bed'))
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/other/path/to/file1.bed'))
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/third/path/to/file1.bed'))
        gSuite.addTrack(GSuiteTrack('ftp://server.somewhere.com/last/path/to/file1.bed'))

        self.assertEqual(['file1.bed', 'file1.bed (2)', 'file1.bed (3)', 'file1.bed (4)'],
                         gSuite.allTrackTitles())


if __name__ == "__main__":
    # TestGSuite().debug()
    unittest.main()
