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

import os

from gold.result.HistoryPresenter import HistoryPresenter
from gold.util.CommonFunctions import isNumber
from quick.util.CommonFunctions import ensurePathExists


class BedGraphPresenter(HistoryPresenter):
    def _writeContent(self, resDictKey, fn):
        ensurePathExists(fn)
        outF = open( fn ,'w')
        outF.write('track type=bedGraph name=' + self._results.getStatClassName() + '_' + resDictKey + \
                   (' viewLimits=0:1 autoScale=off' if resDictKey.lower() in ['pval','p-value'] else '') + os.linesep)
        for bin in self._results.getAllRegionKeys():
            val = str(self._results[bin].get(resDictKey))
            if not isNumber(val) and val not in ['None','nan','.']:
                outF.close()
                os.unlink(fn)
                return
            outF.write( '\t'.join([str(x) for x in \
                        [bin.chr, bin.start, bin.end, str(self._results[bin].get(resDictKey)).replace('None', 'nan')] ]) + os.linesep)
        outF.close()

    def _getSuffix(self):
        return 'bedgraph'
