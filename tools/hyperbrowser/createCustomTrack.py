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

import sys, os, getopt,types

# NB: import eggs before galaxy.util
import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *

import proto.hyperbrowser.hyper_gui as hg

def main():
    filename = sys.argv[1]
    params = hg.fileToParams(filename)
    
    genome = params['dbkey']
    inTrackName = params['track1']
    trackName = params['customname']
    binSize = params['customwinsize']
    method = params['customfunction']
    output = filename
  
    inTracks = None  
    if inTrackName:
        inTracks = inTrackName.split(':')
    
    track = trackName.split(':')
    #funcStr = restore_text(method).replace('XX', '\n')
    funcStr = method
    
    print 'GalaxyInterface.createCustomTrack ',(genome, inTracks, track, binSize, funcStr)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.createCustomTrack(genome, inTracks, track, binSize, funcStr)
    
if __name__ == "__main__":
    main()
