import pkg_resources
import pytest

from pycolocstats.tools import runner
from quick.congloproto.HBCongloMethod import HyperBrowser


@pytest.fixture(scope='function')
def tracks():
    return [pkg_resources.resource_filename('test.quick.congloproto.resources', 'H3K4me1_no_overlaps.bed'),
            pkg_resources.resource_filename('test.quick.congloproto.resources', 'H3K4me3_no_overlaps.bed'),
            pkg_resources.resource_filename('test.quick.congloproto.resources', 'H3K4me1_with_overlaps.bed'),
            pkg_resources.resource_filename('test.quick.congloproto.resources', 'H3K4me3_with_overlaps.bed'),
            pkg_resources.resource_filename('test.quick.congloproto.resources', 'H3K4me1_no_overlaps_cropped.bed'),
            pkg_resources.resource_filename('test.quick.congloproto.resources', 'H3K4me3_no_overlaps_cropped.bed')]

@pytest.mark.usefixtures('tracks')
class TestHBCongloMethod(object):

    def testHBMethod(self, tracks):
        method = HyperBrowser()
        method.setQueryTrackFileNames([tracks[0], tracks[2]])
        method.setReferenceTrackFileNames([tracks[1], tracks[3]])
        method.setGenomeName('hg19')
        method.preserveClumping(True)
        runner.runAllMethodsInSequence([method])
        print method.getFullResults()
