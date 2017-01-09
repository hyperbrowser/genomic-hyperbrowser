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

from gold.description.AnalysisManager import AnalysisManager
import os

STAT_DESCRIPTION_LIST_FN = os.sep.join(['gold', 'description', 'StatDescriptionList.py'])

#analyses = AnalysisManager.getAllAnalyses()
#statClasses = []
#for a in analyses:
#    statClasses += [x.__name__ for x in a._statClassList]
#allStatClassesSet = set(statClasses)

coveredStats = set([line.split('=')[0].strip() for line in open(STAT_DESCRIPTION_LIST_FN) if line.count('=') == 1])

avoidStatSet = set(['RandomizationManagerStat'])

analysisDict = AnalysisManager.getAnalysisDict()

categories = analysisDict.keys()

for cat in categories:
    analyses = analysisDict[cat].values()
    statClasses = []
    for a in analyses:
        statClasses += [x.__name__ for x in a._statClassList]
    allStatClassesSet = set(statClasses)
    uncoveredStatClasses = allStatClassesSet - coveredStats
    missingStatClasses = uncoveredStatClasses - avoidStatSet
    print '#' + cat
    for stat in missingStatClasses:
        print stat + " = ''"