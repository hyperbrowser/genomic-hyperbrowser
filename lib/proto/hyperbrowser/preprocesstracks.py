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
#
# instance is dynamically imported into namespace of <modulename>.mako template (see web/controllers/hyper.py)


import sys
from gold.application.GalaxyInterface import GalaxyInterface
from proto.hyperbrowser.hyper_gui import SelectElement, TrackWrapper
from proto.BaseToolController import *
from HyperBrowserControllerMixin import HyperBrowserControllerMixin


class ToolController(HyperBrowserControllerMixin, BaseToolController):
    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)
        self.genomes = GalaxyInterface.getAllGenomes(self.galaxy.getUserName() \
                                                     if hasattr(self, 'galaxy') else '')
        self.genome = self.params.get('dbkey', self.genomes[0][1])

    def action(self):
        self.genomeElement = SelectElement('dbkey', self.genomes, self.genome)
        self.track = TrackWrapper('track1', GalaxyInterface, [], self.galaxy, [], self.genome)
        self.track.extraTracks = []
        self.track.legend = 'Track'
        self.track.fetchTracks()

    def execute(self):
        self.stdoutToHistory()
        #print self.params
        #tracks = self.params['track1'].split(':')
        username = self.params['userEmail'] if self.params.has_key('userEmail') else ''
        track = self.params['track1'] if self.params.has_key('track1') else []
        print 'GalaxyInterface.startPreProcessing', (self.genome, track, username)
        GalaxyInterface.startPreProcessing(self.genome, track, username)


def getController(transaction = None, job = None):
    return ToolController(transaction, job)

