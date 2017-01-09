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

from gold.track.GenomeRegion import GenomeRegion
from gold.track.Track import Track
from gold.statistic.AllStatistics import CountStat, MeanStat, ZipperStat
from gold.origdata.GenomeElementSource import GenomeElementSource
from quick.postprocess.GlobalCollectorPP import GlobalCollectorPP
from quick.postprocess.XBinnerPP import XBinnerPP
from quick.postprocess.HistBinnerPP import HistBinnerPP
from quick.postprocess.YSummarizerPP import YSummarizerPP
#from pylab import *
from stats import lmean


def _getRegion(chr, start, end):
    return GenomeRegion('old_NCBI','chr'+str(chr), start, end)

def runIntegrationTest():    
    track = Track(['melting'])
    track2 = Track(['melting'])
    geSource = GenomeElementSource('/usit/titan/u1/bjarnej/new_hb','old_NCBI')

    print geSource

    coll = GlobalCollectorPP(geSource, track, track2, ZipperStat, CountStat, MeanStat)

    coll = XBinnerPP(coll, 5)
#    for x,y in coll:
#        print x,y

    coll = YSummarizerPP(coll, lmean)
    
    results = [[result[i] for result in coll] for i in range(2)]
    print results

    slide = 3

    x = results[0]
    y = results[1]
    for i in range(len(x)-(slide-1)):
        print (y[i] + y[i+1] + y[i+2])/slide


#    plot(results[0],results[1])
#   show()



    #
    #coll = GlobalCollectorPP(geSource, track, track2, ZipperStat, CountStat, MeanStat)
    #print coll
    #results = [[floor(result[i]) for result in coll] for i in range(2)]
    #print results
    #coll2 = HistBinnerPP(coll, 1)
    #print coll2
    #bins = [result[0] for result in coll2]
    #print bins
    #bins.append(max(bins) + 1)
    #n, bins, patches = hist(results[1], bins)
    #
    #show()


if __name__ == "__main__":
    runIntegrationTest()


