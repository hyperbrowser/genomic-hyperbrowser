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

from gold.track.Track import Track
from gold.track.GenomeRegion import GenomeRegion
from gold.track.TrackFormat import TrackFormatReq

if __name__ == "__main__":
    track = Track(['test'])
    #trackView = track.getTrackView(None, GenomeRegion('hg18','chrM',1000,10000))
    #trackView2 = track.getTrackView(None, GenomeRegion('hg18','chrM',4000,4000))
    trackView = track.getTrackView(GenomeRegion('TestGenome','chr1',-1,1000))

    count=0
    for el in trackView:
        print el.start(), el.end()
        count+=1
        if count>50:
            break
        
    print len([el for el in trackView])
    #print len([el for el in trackView2])
    
    