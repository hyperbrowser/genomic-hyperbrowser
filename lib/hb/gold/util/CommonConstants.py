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

from collections import OrderedDict

BINARY_MISSING_VAL = -1

RESERVED_PREFIXES = OrderedDict([(x, None) for x in ('start', 'end', 'val', 'strand', 'id', 'edges', 'weights')])

LICENSE_STMT = \
    '''# Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
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

'''

TRACK_TITLES_SEPARATOR = '|||'

STATISTIC_CLASS_NAME_TO_NATURAL_NAME_DICT = \
    dict(CountNumSegmentsStat='Nr. of segments in track',
         CountElementStat='Nr. of reference track elements',
         CountSegmentsOverlappingWithT2Stat='Nr. of overlapping segments with query track',
         CountStat='Genome coverage of track (bps)',
         SingleValueOverlapStat='Overlap between query and reference track (bps)')

BATCH_COL_SEPARATOR = '|'
MULTIPLE_EXTRA_TRACKS_SEPARATOR = '&'
