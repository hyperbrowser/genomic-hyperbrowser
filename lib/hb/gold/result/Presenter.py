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

from gold.util.CustomExceptions import AbstractClassError
'''
Presenter is the root class and absolute superclass for all presenter-classes
It has two instance variables:
    _results: a Results object containing all results data from an analysis run(subclass of dict)
    _baseDir: the filepath to the folder where the history-item is saved
'''
class Presenter(object):
    def __init__(self, results, baseDir=None):
        self._results = results
        self._baseDir = baseDir
    
    def getDescription(self):
        raise AbstractClassError
        
    def getReference(self, resDictKey):
        raise AbstractClassError

    #TODO: refactor all presenters to use StaticFile. Then remove the following convenience method:
    def _getRelativeURL(self, fullFn):
        import os.path
        
        baseDirForRelativeUrl = self._baseDir.rstrip(os.path.sep)
        if os.path.split(baseDirForRelativeUrl)[-1].isdigit(): #ResultsViewerCollection
            baseDirForRelativeUrl = os.path.dirname(baseDirForRelativeUrl)

        if fullFn.startswith(baseDirForRelativeUrl + os.path.sep):
            return fullFn[len(baseDirForRelativeUrl) + 1:]

#mal:
    #def __init__(self, results, baseDir=None):
    #    Presenter.__init__(results, baseDir)
    #
    #def getDescription(self):
    #    
    #def getReference(self, resDictKey):
