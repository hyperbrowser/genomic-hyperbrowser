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
'''
Created on May 18, 2015

@author: boris
'''

    
def normalizeMatrixData(plotData):
    transposed = [list(x) for x in zip(*plotData)]
    transposedNormalized = []
    for row in transposed:
        maxRow = max(row)
        if maxRow == 0:
            maxRow = 1
        transposedNormalized.append([1.0*x/maxRow for x in row])
    return [list(x) for x in zip(*transposedNormalized)]