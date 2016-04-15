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

from gold.result.ResultsViewer import ResultsViewerCollection
from gold.application.GalaxyInterface import GalaxyInterface
import cPickle
import functools
import gold.description.Analysis
from quick.application.UserBinSource import MinimalBinSource

gold.description.Analysis.MinimalBinSource = \
    functools.partial(MinimalBinSource, genome='TestGenome')

#res = GalaxyInterface.run(["segsLen1"],["segs"],'Raw -> RawOverlapStat','TestGenome:chr1:1-4001','2000','TestGenome')
#cPickle.dump(res, open('ResultSandbox.pickle','w'))
res = cPickle.load(open('ResultSandbox.pickle'))
print ResultsViewerCollection([res],'/Users/sandve/DATA/__div/tempBaseDir/')
