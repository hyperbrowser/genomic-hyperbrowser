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

#!/usr/bin/env python
import os
from gold.application.GalaxyInterface import GalaxyInterface
from quick.extra.FunctionCategorizer import FunctionCategorizer

def extremeMelt(val,diff):
    if val < 55:
        return -1
    elif val > 85:
        return 1

def meltSeg(val,diff):
    if diff < -0.13:
        return -2
    elif diff > 0.13:
        return 2
    elif -0.01 <= diff <= 0.01:
        return 0
    else:
        return None

meltSegLines = '''
    if diff < -0.13:
        return -2
    elif diff > 0.13:
        return 2
    elif -0.01 <= diff <= 0.01:
        return 0
    else:
        return None
'''.split(os.linesep)

#FunctionCategorizer(['melting'], meltSeg).createNewTrack(['melting','meltMapSeg'])
GalaxyInterface.createSegmentation('hg18',['melting'], ['melting','meltMapSeg2'], meltSegLines)
#exec( os.linesep.join( ['def categorizerMethod(val,diff):'] + meltSegLines) )
#a = categorizerMethod
#print a(3,-1)


