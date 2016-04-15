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

#from quick.origdata.PreProcGenerator import PreProcGenerator
from gold.statistic.AllStatistics import RawOverlapStat
from quick.application.AutoBinner import AutoBinner
from gold.track.Track import Track
from gold.track.GenomeRegion import GenomeRegion
from config.Config import DEFAULT_GENOME
from gold.application.StatRunner import StatRunner
from gold.application.GalaxyInterface import GalaxyInterface
from quick.application.UserBinSource import parseRegSpec
import profile
import pstats

#PreProcGenerator.generateTrack(['genes'])
from gold.application.GalaxyInterface import GalaxyInterface

#GalaxyInterface.run(['hpv_200kb'], ['allTss'], RawOverlapStat)
def oldTest():
    results = []
    for chr in ['chr'+str(i) for i in range(1,21)]:
        userBinSource = AutoBinner(parseRegSpec(chr, DEFAULT_GENOME), 1e9) #fixme: do a conversion from  binSpecification to binSource..
        trackName1 = ['hpv_200kb']
        trackName2 = ['allTss']
        #trackName2 = ['melting','zvals','11mers']
        #trackName2 = ['melting']
        #trackName1 = ['melting']
        res = StatRunner.run(userBinSource , Track(trackName1), Track(trackName2), RawOverlapStat)
        results.append( res[0] )
        print res
        
    globResults = {}
    for key in results[0]:
        globResults[key] = sum(res[key] for res in results)
    print globResults
    tp,fp,tn,fn = [globResults[key] for key in 'TP,FP,TN,FN'.split(',')]
    print 'freq near HPV: ', 1.0* tp / (tp+fp)
    print 'freq far from HPV: ', 1.0* fn / (tn+fn)
    
def newTest():
    #GalaxyInterface.run(['genes','TSS'],['hpv_200kb'],'TpReshuffledStat','chr20:10000000-15000000,5000000')
    profile.run(  "GalaxyInterface.run(['genes','TSS'],['hpv_200kb'],'TpReshuffledStat','chr20:10000000-15000000,5000000')",'myProf.txt')
    p = pstats.Stats('myProf.txt')
    p.sort_stats('time').print_stats(50)
    
newTest()   
