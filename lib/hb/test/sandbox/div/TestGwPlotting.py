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

from proto.RSetup import r
from config.Config import HB_SOURCE_CODE_BASE_DIR
import os

PLOT_BED_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'plotBed.r'])
PLOT_CHR_FN = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'rCode', 'ChromosomePlot.r'])
OUTPUT_PATH = os.sep.join([HB_SOURCE_CODE_BASE_DIR, 'data'])

r('source("%s")' % PLOT_BED_FN)
r('source("%s")' % PLOT_CHR_FN)
r('loadedBedData <- plot.bed("/xanadu/home/geirksa/_data/test.wig")')
print len(r['loadedBedData'])
#r('plot.chrom(segments=loadedBedData, dir.print="%s", data.unit="bp")' % OUTPUT_PATH)
r('plot.chrom(segments=loadedBedData, data.unit="bp", dir.print="/hyperdata")')
