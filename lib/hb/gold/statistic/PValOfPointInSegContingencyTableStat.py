## Copyright (C) 2009, Geir Kjetil Sandve, Sveinung Gundersen and Morten Johansen
## This file is part of The Genomic HyperBrowser.
##
##    The Genomic HyperBrowser is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    The Genomic HyperBrowser is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with The Genomic HyperBrowser.  If not, see <http://www.gnu.org/licenses/>.
#
#from gold.statistic.MagicStatFactory import MagicStatFactory
#from gold.statistic.Statistic import Statistic
#from proto.RSetup import r
#from gold.statistic.CategoryPointCountInSegsMatrixStat import CategoryPointCountInSegsMatrixStat
#from quick.statistic.CategoryPointCountNoOverlapsStat import CategoryPointCountNoOverlapsStat
#
#import numpy
#
#class PValOfPointInSegContingencyTableStat(MagicStatFactory):
#    pass
#
##class PValOfPointInSegContingencyTableStatSplittable(StatisticSumResSplittable):
##    pass
#            
#from gold.util.CommonFunctions import repackageException
#class PValOfPointInSegContingencyTableStatUnsplittable(Statistic):
#    @repackageException(Exception,RuntimeError)
#    def _compute(self):
#        res = self._children[0].getResult()['Result']
#        rowNames = res['Rows']
#        
#        O = numpy.array( res['Matrix'] )
#        S = O.sum(axis=0)
#        
#        N =  self._children[1].getResult()
#        Ntotal = sum( N.values() )
#        
#        pval = numpy.zeros(O.shape, dtype='d')
#        for i in range(O.shape[0]):
#            for j in range(O.shape[1]):
#                #prepare vars for r-call:
#                x = q = O[i][j]
#                m = S[j]
#                n = Ntotal - m
#                k = N[ rowNames[i] ]
#                rawPval = min( r.phyper(q,m,n,k), r.phyper(q,m,n,k,False)+r.dhyper(x,m,n,k) )
#                pval[i][j] = min(rawPval*2, 1) #correct for two-tail..
#        
#        return pval
#        
#    
#    def _createChildren(self):
#        #kwArgs = copy(self._kwArgs)
#        self._addChild( CategoryPointCountInSegsMatrixStat(self._region, self._track, self._track2, **self._kwArgs) )
#        self._addChild( CategoryPointCountNoOverlapsStat(self._region, self._track) )
