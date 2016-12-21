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
#import galaxy.eggs
#from galaxy.util import restore_text

from gold.application.GalaxyInterface import *
from config.Config import URL_PREFIX

import proto.hyperbrowser.hyper_gui as hg

def main():
    #print "running"
    filename = sys.argv[1]
    params = hg.fileToParams(filename)
    
    batch = params['batch'].split('\n')
    genome = params['dbkey']

    sys.stdout = open(filename, "w", 0)

    username = params['userEmail'] if params.has_key('userEmail') else ''
    GalaxyInterface.runBatchLines(batch, filename, genome, username)
    
if __name__ == "__main__":
    os.nice(10)
    main()
