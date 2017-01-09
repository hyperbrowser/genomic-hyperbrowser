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

class BedGraphComposer(FileFormatComposer):
    FILE_SUFFIXES = ['bedgraph']
    FILE_FORMAT_NAME = 'bedGraph'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() \
                                 and trackFormat.getValTypeName() in ['Number', 'Number (integer)'], \
                           trackFormatName='valued segments')

    # Compose methods
    
    def _compose(self, out):
        trackName = self._geSource.getTrackName()
        if trackName is not None:
            name = ':'.join(self._geSource.getTrackName()).replace(' ','_')
        else:
            name = None
        
        print >>out, 'track type=bedGraph' + (' name=%s' % name if name is not None else '')

        for ge in self._geSource:
            cols = [''] * 4
            
            cols[0] = ge.chr
            cols[1] = ge.start
            cols[2] = ge.end
            cols[3] = self._formatVal(ge.val)
            
            print >>out, '\t'.join([str(x) for x in cols])
            
    def _formatVal(self, value):
        return self._commonFormatNumberVal(value)

class BedGraphTargetControlComposer(BedGraphComposer):
    FILE_SUFFIXES = ['targetcontrol.bedgraph']
    FILE_FORMAT_NAME = 'target/control bedGraph'
    
    @staticmethod
    def matchesTrackFormat(trackFormat):
        return MatchResult(match=trackFormat.isInterval() and not trackFormat.isDense() \
                                 and trackFormat.getValTypeName() == 'Case-control', \
                           trackFormatName='valued segments')
            
    def _formatVal(self, value):
        return self._commonFormatBinaryVal(value)