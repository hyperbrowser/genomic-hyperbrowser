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
from gold.util.CommonFunctions import strWithStdFormatting

class GlobalValuePresenter(Presenter):
    def __init__(self, results, baseDir=None):
        Presenter.__init__(self, results, baseDir)

    def getDescription(self):
        return 'Summary'
        
    def getReference(self, resDictKey):
        globalRes = self._results.getGlobalResult()
        return strWithStdFormatting( globalRes[resDictKey] ) if globalRes not in [None,{}] else 'None'

class ForgivingGlobalValuePresenter(GlobalValuePresenter):
    def getTrackName(self, trackIndex):
        return self._results.getTrackNames()[trackIndex]
    
    def getReference(self, resDictKey):
        globalRes = self._results.getGlobalResult()
        if globalRes is None:
            return 'N/A'
        elif resDictKey in globalRes:
            return GlobalValuePresenter.getReference(self, resDictKey)
        else:
            return ''


