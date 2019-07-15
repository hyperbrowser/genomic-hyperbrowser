__author__ = 'skh'

from quick.metadata import GenomeInfo
from gtrackcore.track.core.GenomeRegion import GenomeRegion
import numpy as np

import timeit
import time

def generateTrack(niceness=10, values=False):
    """
    Generate two worst case point tracks
    :param niceness: int. Divide the length of chr1 with this number. The
    large the number the smaller the generated track. Default is 10

    File size will be quite large (>1gb) for niceness smaller the 10.

    This method creates two "worst case" point tracks. The first one
    contains only odd numbered positions (1,3,..., len(chr1)). The second one
    contains only even numbered positions (0,2,4,...,len(chr1)).
    :return: Two worst case point tracks writen to disk.
    """

    hg18 = list((GenomeRegion('hg18', c, 0, l)
                 for c, l in GenomeInfo.GENOMES['hg18']['size'].iteritems()))

    chr1 = (GenomeRegion('hg18', 'chr1', 0,
            GenomeInfo.GENOMES['hg18']['size']['chr1']))
    createTime = int(time.time())

    headerP = ("##gtrack version: 1.0\n"
               "##track type: points\n"
               "##uninterrupted data lines: true\n"
               "##sorted elements: true\n"
               "##no overlapping elements: true\n"
               "###seqid\tstart\n")

    headerVP = ("##gtrack version: 1.0\n"
                "##track type: valued points\n"
                "##uninterrupted data lines: true\n"
                "##sorted elements: true\n"
                "##no overlapping elements: true\n"
                "###seqid\tstart\tvalue\n")

    start = timeit.default_timer()
    with open("./test_tracks/p-odd-{0}.gtrack".format(createTime), 'w+') as \
            point:

        print("Starting generation odd track of {0}".format(chr1.chr))
        length = len(chr1)/niceness
        positions = range(1, length, 2)

        if values:
            point.write(headerVP)
            print("Starting to generate random values")
            randStart = timeit.default_timer()
            val = np.random.random((length, 1))
            randEnd = timeit.default_timer()
            print("Finished generating random values")
            print("Random generation runtime: {0}".format(randEnd-randStart))

            for position, v in zip(positions, val):
                out = "{0}\t{1}\t{2}\n".format(chr1.chr, position, v[0])
                point.write(out)
        else:
            point.write(headerP)
            for position in positions:
                out = "{0}\t{1}\n".format(chr1.chr, position)
                point.write(out)

    with open("./test_tracks/p-even-{0}.gtrack".format(createTime), 'w+') as \
            point:
        print("Starting generation even track of {0}".format(chr1.chr))
        length = len(chr1)/niceness
        positions = range(0, length, 2)

        if values:
            point.write(headerVP)
            print("Starting to generate random values")
            randStart = timeit.default_timer()
            val = np.random.random((length, 1))
            randEnd = timeit.default_timer()
            print("Finished generating random values")
            print("Random generation runtime: {0}".format(randEnd-randStart))

            for position, v in zip(positions, val):
                out = "{0}\t{1}\t{2}\n".format(chr1.chr, position, v[0])
                point.write(out)
        else:
            point.write(headerP)
            for position in positions:
                out = "{0}\t{1}\n".format(chr1.chr, position)
                point.write(out)

    end = timeit.default_timer()
    print("Generation finished! Total time {0}".format(end-start))

if __name__ == '__main__':
    generateTrack(10, values=True)
