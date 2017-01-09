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

from gold.origdata.GtrackGenomeElementSource import GtrackGenomeElementSource
from gold.origdata.GtrackComposer import StdGtrackComposer, ExtendedGtrackComposer
from gold.origdata.GtrackHeaderExpander import expandHeadersOfGtrackFileAndReturnComposer
from gold.origdata.GESourceWrapper import ElementModifierGESourceWrapper
from gold.util.CustomExceptions import ShouldNotOccurError
from quick.origdata.FullInfoDict import IdFullInfoDict, TupleFullInfoDict

class ElementComplementer(ElementModifierGESourceWrapper):
    def __init__(self, geSource, fullDbDict, gtrackColsToAdd):
        self._prefixesToAdd = [GtrackGenomeElementSource.convertNameFromGtrack(col) for col in gtrackColsToAdd]
        if 'edges' in self._prefixesToAdd:
            self._prefixesToAdd.append('weights')
            
        ElementModifierGESourceWrapper.__init__(self, geSource)
        
        self._fullDbDict = fullDbDict
        self._prefixList = geSource.getPrefixList() + self._prefixesToAdd
        
    def _next(self, brt, ge, i):
        for prefix in self._prefixesToAdd:
            dbGE = self._fullDbDict.get(ge)
            if prefix == 'weights' and (dbGE is None or dbGE.get('edges') is None):
                continue
            setattr(ge, prefix, dbGE.get(prefix) if dbGE is not None else '.')
        return ge
        
    def getPrefixList(self):
        return self._prefixList

def _commonComplementGtrackFile(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome):
    origGESource = GtrackGenomeElementSource(origFn, genome)
    dbGESource = GtrackGenomeElementSource(dbFn, genome)
    
    dbPrefixes = dbGESource.getPrefixList()

    if intersectingFactor == 'id':
        fullDbDict = IdFullInfoDict(dbGESource, dbPrefixes)
    elif intersectingFactor == 'position':
        fullDbDict = TupleFullInfoDict(dbGESource, dbPrefixes)
    else:
        ShouldNotOccurError
        
    forcedHeaderDict = {}
    dbHeaderDict = dbGESource.getHeaderDict()
    
    if 'value' in gtrackColsToAdd:
        forcedHeaderDict['value type'] = dbHeaderDict['value type']
        forcedHeaderDict['value dimension'] = dbHeaderDict['value dimension']
    if 'edges' in gtrackColsToAdd:
        forcedHeaderDict['edge weight type'] = dbHeaderDict['edge weight type']
        forcedHeaderDict['edge weight dimension'] = dbHeaderDict['edge weight dimension']
    
    composerCls = ExtendedGtrackComposer if origGESource.isExtendedGtrackFile() else StdGtrackComposer    
    composedFile = composerCls( ElementComplementer(origGESource, fullDbDict, gtrackColsToAdd), \
                                forcedHeaderDict=forcedHeaderDict).returnComposed()
        
    return expandHeadersOfGtrackFileAndReturnComposer('', genome, strToUseInsteadOfFn=composedFile)
        
def complementGtrackFileAndReturnContents(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome=None):
    return _commonComplementGtrackFile(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome).returnComposed()
    
def complementGtrackFileAndWriteToFile(origFn, dbFn, outFn, intersectingFactor, gtrackColsToAdd, genome=None):
    return _commonComplementGtrackFile(origFn, dbFn, intersectingFactor, gtrackColsToAdd, genome).composeToFile(outFn)
