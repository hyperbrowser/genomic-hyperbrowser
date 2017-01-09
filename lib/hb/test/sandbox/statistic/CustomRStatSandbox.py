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

from gold.application.GalaxyInterface import GalaxyInterface
import os
import tempfile
import sys
from quick.result.ResultsCollection import ResultsCollection
from gold.statistic.CustomRStat import CustomRStat, CustomRStatUnsplittable
from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from quick.application.UserBinSource import UserBinSource
from gold.application.StatRunner import StatRunner
from quick.util.CommonFunctions import wrapClass
import urllib

#f = tempfile.NamedTemporaryFile()
#scriptLines = ['result <- sum(track1[,3])','2']

#scriptLines = ['return( sum(track1[3,]) )']
#scriptLines = ['return( sum(track1[3,]) )']
#scriptLines = ['return( sum(track1[3,]) + mean(track2[3,]) )']
scriptLines = ['a=track1[2,1]-track1[1,1]', 'b=track2[2,1]-track2[1,1]', 'return(a-b)']

fn = '/usit/titan/u1/geirksa/_data/rTempScript.txt'
open(fn,'w').writelines( [line+os.linesep for line in scriptLines] )
fn = fn.encode('hex_codec')

#
#for line in scriptLines:
#    f.write(line + os.linesep)
#f.flush()
#print f.name

def test1():
    #myTrack = Track(['melting'])
    #myTrack2 = Track(['curvature'])
    myTrack = Track(['genes','refseq'])
    myTrack2 = Track(['repeats'])
                     
    rStat = CustomRStatUnsplittable(GenomeRegion('hg18','chr1',0,100000000), myTrack, myTrack2, scriptFn = fn)
    #rStat._codeLines = scriptLines
    #rStat.compute()
    print rStat.getResult()

def test2():
    myTrack = Track(['melting'])
    myTrack2 = Track(['genes','refseq'])
    userBinSource = UserBinSource('chr1:0-10','10')
    
    res = StatRunner.run(userBinSource, myTrack, myTrack2, wrapClass(CustomRStat, {'scriptFn':fn}))
    resColl = ResultsCollection()
    resColl.addResults(None, res)
    print resColl.getHtmlString()

def test3():
    GalaxyInterface.run(['repeats','SINE'],['repeats'],\
                        '[scriptFn:='+fn+':] -> CustomRStat',\
                        'chr1:1-100000000','10m')
    
#test1()
#test2()
test3()
