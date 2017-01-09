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

import galaxy.eggs
from galaxy.util import restore_text

from gold.application.GalaxyInterface import *


def main():
    input = sys.argv[1]
    output = sys.argv[2]
    criteria = sys.argv[3]
    genome = sys.argv[4]
    
    criteria = restore_text(criteria).replace('XX', '\n')

    print 'GalaxyInterface.filterMarkedSegments', (input, output, criteria, genome)
    sys.stdout = open(output, "w", 0)
    GalaxyInterface.filterMarkedSegments(input, output, criteria, genome)
    
if __name__ == "__main__":
    main()
