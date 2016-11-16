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

from config.Config import MAX_LOCAL_RESULTS_IN_TABLE
from gold.result.Presenter import Presenter
from gold.util.CommonFunctions import strWithStdFormatting
from proto.hyperbrowser.HtmlCore import HtmlCore
from quick.util.CommonFunctions import ensurePathExists


class RawTextTablePresenter(Presenter):
    def __init__(self, results, baseDir, header):
        Presenter.__init__(self, results, baseDir)
        self._fn = os.sep.join([baseDir, 'table.txt'])
        self._writeContent(self._fn, header)

    def getDescription(self):
        return 'Raw text table (all)'
    
    def getReference(self, resDictKey):
        return HtmlCore().link('View', self._getRelativeURL(self._fn))

    def _writeContent(self, fn, header):
        #core = HtmlCore()
        
        #core.begin()
        #core.bigHeader(header)
        #core.header('Local result table')
        text = ''
        if len( self._results.getAllRegionKeys() ) > MAX_LOCAL_RESULTS_IN_TABLE:
            text += 'Local results were not printed because of the large number of bins: ' \
                  + str(numUserBins) + ' > ' + str(MAX_LOCAL_RESULTS_IN_TABLE)
        else:
            #core.tableHeader([ str( HtmlCore().textWithHelp(baseText, helpText) ) for baseText, helpText in 
            #                  ([('Region','')] + self._results.getLabelHelpPairs()) ])
            
            for regionKey in self._results.getAllRegionKeys():
                text += '\t'.join([str(regionKey)] +\
                    [ strWithStdFormatting( self._results[regionKey].get(resDictKey) ) \
                     for resDictKey in self._results.getResDictKeys() ]) + os.linesep
            #core.tableFooter()

        #core.end()
        
        ensurePathExists(fn)        
        open(fn,'w').write( text )
