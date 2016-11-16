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
from proto.hyperbrowser.TextCore import TextCore
from quick.util.CommonFunctions import ensurePathExists


class TableFromDictOfDictsPresenter(Presenter):
    def __init__(self, results, baseDir, header):
        Presenter.__init__(self, results, baseDir)

        self._htmlFns = {}
        self._rawFns = {}
        
        for resDictKey in self._results.getResDictKeys():
            #HTML
            self._htmlFns[resDictKey] = os.sep.join([baseDir, resDictKey + '_table.html'])
            self._writeContent(self._htmlFns[resDictKey], header, resDictKey, HtmlCore)
            #Raw text
            self._rawFns[resDictKey] = os.sep.join([baseDir, resDictKey + '_table.txt'])
            self._writeContent(self._rawFns[resDictKey], header, resDictKey, TextCore)

    def getDescription(self):
        return 'Tables: values per bin'
    
    def getReference(self, resDictKey):
        return str(HtmlCore().link('HTML', self._getRelativeURL(self._htmlFns[resDictKey]))) + \
               '&nbsp;\&nbsp;' + \
               str(HtmlCore().link('Raw&nbsp;text', self._getRelativeURL(self._rawFns[resDictKey])))

    def _getKeys(self, resDictKey):
        keys = set([])
        for regionKey in self._results.getAllRegionKeys():
            res = self._results[regionKey].get(resDictKey)
            if isinstance(res, dict):
                for key in res.keys():
                    keys.add(key)
        return keys

    def _writeContent(self, fn, header, resDictKey, coreCls):
        keys = self._getKeys(resDictKey)

        core = coreCls()
        
        core.begin()
        core.bigHeader(header)
        core.header('Local result table for ' + resDictKey)
        
        if len( self._results.getAllRegionKeys() ) > MAX_LOCAL_RESULTS_IN_TABLE:
            core.line('Local results were not printed because of the large number of bins: ' \
                  + str(numUserBins) + ' > ' + str(MAX_LOCAL_RESULTS_IN_TABLE))
        else:
            core.tableHeader([ str( coreCls().textWithHelp(baseText, helpText) ) for baseText, helpText in 
                              ([('Region','')] + [self._results.getLabelHelpPair(key) for key in keys]) ])
            
            for regionKey in self._results.getAllRegionKeys():
                if  self._results[regionKey].get(resDictKey) is None:
                    core.tableLine([str(regionKey)] + [None]*len(keys))
                else:
                    core.tableLine([str(regionKey)] +\
                                   [ strWithStdFormatting( self._results[regionKey][resDictKey].get(key) ) for key in keys])
            core.tableFooter()

        core.end()
        
        ensurePathExists(fn)        
        open(fn,'w').write( str(core) )
