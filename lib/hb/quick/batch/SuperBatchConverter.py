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

from quick.application.ProcTrackOptions import ProcTrackOptions
from config.Config import DEFAULT_GENOME
from gold.util.CommonConstants import BATCH_COL_SEPARATOR
from urllib import quote, unquote

class SuperBatchConverter:
    @classmethod
    def super2batch(cls, lines, genome):
        return reduce(lambda x,y:x+y, [cls.superLine2batch(line, genome) for line in lines])
    
    @classmethod
    def superLine2batch(cls, line, genome):
        if line.strip() == '' or line[0]=='#':
            return []
        
        cols = line.split(BATCH_COL_SEPARATOR)

        if len(cols) == 4:
            cols = cols[:3] + ['dummy', cols[3]]
            line = BATCH_COL_SEPARATOR.join(cols)
        
        from quick.batch.BatchRunner import BatchRunner
        #errorResult, userBinSource  = BatchRunner._constructBins(cols[0], cols[1], genome)
        #if errorResult is not None:
        #    return [BATCH_COL_SEPARATOR.join([ 'dummy', cols[0], cols[1], 'dummyTN1', 'dummyTN2', 'dummyStatName' ])]
        
        for colIndex, col in zip(range(2,5), cols[2:5]): #not binSpec, but tn1, tn2, statistic..
            if '/' in col:
                splitPoint = col.find('/')
                splittedCols = col[0:splitPoint], col[splitPoint+1:]
                splittedListLines = [ cols[0:colIndex] +[splitCol]+ cols[colIndex+1:]\
                    for splitCol in splittedCols]
                #1+''
                return reduce(lambda x,y:x+y, [cls.superLine2batch(BATCH_COL_SEPARATOR.join(line), genome) for line in splittedListLines])
        for colIndex, col in zip(range(2,4), cols[2:4]):
            if '*' in col:
                typeParts = col.split(':')
                assert typeParts[-1]=='*' and not any('*' in part for part in typeParts[:-1])
                #whitespacedTrackName = [x.replace('_',' ') for x in typeParts[:-1]]
                
                unquotedTrackName = [unquote(x) for x in typeParts[:-1]]
                #print 'TEMP: ',genome, unquotedTrackName
                starOptions = ProcTrackOptions.getSubtypes(genome, unquotedTrackName, True)
                if len(starOptions) == 0:
                    raise Exception('No subtracks for parent track: %s' % str(unquotedTrackName))
                                                   
                #typeOptions = [':'.join(typeParts[:-1] + [starOpt.replace(' ','_')]) for starOpt in starOptions]
                typeOptions = [':'.join(typeParts[:-1] + [quote(starOpt)]) for starOpt in starOptions]
                                
                splittedCols = typeOptions
                splittedListLines = [ cols[0:colIndex] +[splitCol]+ cols[colIndex+1:]\
                    for splitCol in splittedCols]
                return reduce(lambda x,y:x+y, [cls.superLine2batch(BATCH_COL_SEPARATOR.join(line), genome) for line in splittedListLines])
            
        
        return [cls.generateBatchName(line)+BATCH_COL_SEPARATOR+line]

    @staticmethod
    def generateBatchName(line):
        cols = line.split(BATCH_COL_SEPARATOR)        
        return '_'.join(cols[2:5])
    
#print SuperBatchConverter.super2batch(['* * a/b c/d stat','* * e f stat1/stat2'])
#print SuperBatchConverter.super2batch(['* * bs hpv:* stat'])

