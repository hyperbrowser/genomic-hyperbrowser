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

import cProfile
import profile
import pstats

from quick.util.PstatsUtil import OverheadStats
from quick.util.StaticFile import GalaxyRunSpecificFile
from gold.result.HtmlCore import HtmlCore
from quick.util.CommonFunctions import ensurePathExists

class Profiler:
    PROFILE_HEADER = '--- Profile ---'
    PROFILE_FOOTER = '--- End Profile ---'

    def __init__(self):
        self._prof = cProfile.Profile()
        self._stats = None

    def run(self, runStr, globals, locals):
        self._prof = self._prof.runctx(runStr, globals, locals)
        self._stats = pstats.Stats(self._prof)

    def start(self):
        self._prof.enable()

    def stop(self):
        self._prof.disable()
        self._stats = pstats.Stats(self._prof)

    def printStats(self):
        if self._stats == None:
            return
        
        print Profiler.PROFILE_HEADER
        self._stats.sort_stats('cumulative')
        self._stats.print_stats()
        print Profiler.PROFILE_FOOTER
        
        print Profiler.PROFILE_HEADER
        self._stats.sort_stats('time')
        self._stats.print_stats()
        print Profiler.PROFILE_FOOTER

    def printLinkToCallGraph(self, id, galaxyFn, prune=True):
        statsFile = GalaxyRunSpecificFile(id + ['pstats.dump'], galaxyFn)
        dotFile = GalaxyRunSpecificFile(id + ['callGraph.dot'], galaxyFn)
        pngFile = GalaxyRunSpecificFile(id + ['callGraph.png'], galaxyFn)
        
        ensurePathExists(statsFile.getDiskPath())
        
        self._stats.dump_stats(statsFile.getDiskPath())
        stats = OverheadStats(statsFile.getDiskPath())
        stats.writeDotGraph(dotFile.getDiskPath(), prune=prune)
        stats.renderGraph(dotFile.getDiskPath(), pngFile.getDiskPath())
        
        print str(HtmlCore().link('Call graph based on profiling (id=%s)' % ':'.join(id), pngFile.getURL()))
