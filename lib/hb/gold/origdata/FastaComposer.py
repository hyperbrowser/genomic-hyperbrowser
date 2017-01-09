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

from gold.origdata.FileFormatComposer import FileFormatComposer, MatchResult
from gold.track.TrackFormat import TrackFormat
from gold.origdata.GEDependentAttributesHolder import iterateOverBRTuplesWithContainedGEs

class FastaComposer(FileFormatComposer):
    FILE_SUFFIXES = ['fasta', 'fas', 'fa']
    FILE_FORMAT_NAME = 'FASTA'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.reprIsDense() and trackFormat.getValTypeName() == 'Character', \
                           trackFormatName='function')

    # Compose methods
    
    def _compose(self, out):
        
        for brt, geList in iterateOverBRTuplesWithContainedGEs(self._geSource):
            chr, startEnd = str(brt.region).split(':')
            print >> out, '>%s %s' % (chr, startEnd)
             
            line = ''
            for i, ge in enumerate(geList):
                line += ge.val
                if (i+1) % 60 == 0:
                    print >> out, line
                    line = ''
            
            if i+1 % 60 != 0:
                print >> out, line