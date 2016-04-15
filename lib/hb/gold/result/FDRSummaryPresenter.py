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

from gold.result.Presenter import Presenter

class FDRSummaryPresenter(Presenter):
    def __init__(self, results, baseDir=None):
        Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'Significance at 20% FDR'
        
    def getReference(self, resDictKey):
        numTotal = len(self._results)
        numSign = self._results.getNumSignificantAdjustedPVals(resDictKey, 0.20, 'fdr')
        if numSign is None:
            return '' #'N/A'
        else:
            return str(numSign) + '/' + str(numTotal) + ' bins'
