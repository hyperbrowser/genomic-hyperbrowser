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

from gold.application.GalaxyInterface import *

import proto.hyperbrowser.hyper_gui as hg

def main():
    #print "running"
    filename = sys.argv[1]
    params = hg.fileToParams(filename)
    
    trackIn = params['intrack'].split(':')
    trackOut = params['outtrack'].split(':')
    methodLines = params['method'].split('\n')
    segLength = params['min_length']
    genome = params['dbkey']
    username = params['userEmail'] if params.has_key('userEmail') else ''

    print 'GalaxyInterface.createSegmentation', (genome, trackIn, trackOut, methodLines, segLength)
    sys.stdout = open(filename, "w", 0)

    GalaxyInterface.createSegmentation(genome, trackIn, trackOut, methodLines, segLength, username)

    
if __name__ == "__main__":
    main()
