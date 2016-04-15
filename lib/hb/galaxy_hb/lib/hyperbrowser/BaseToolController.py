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

import sys
from gold.application.GalaxyInterface import GalaxyInterface
from collections import OrderedDict
from hyper_gui import *

class BaseToolController(object):
    def __init__(self, trans = None, job = None):
        if trans:
            self.openTransaction(trans)
        elif job:
            self.openJobParams(job)

    def openTransaction(self, trans):
        self.transaction = trans
        self.galaxy = GalaxyWrapper(trans)
        self.params = self.galaxy.params

    def openJobParams(self, file):
        #self.galaxy = None
        self.jobFile = file
        self.json_params, self.params = load_input_parameters(self.jobFile, False)
        if self.params.has_key('tool_name'):
            self.params['tool_id'] = self.params['tool_name']

    def action(self):
        'to be called from mako'
        pass

    def execute(self):
        'to be called from job-script'
        pass

    def stdoutToHistory(self):
        sys.stdout = open(self.jobFile, "w", 0)

    def stdoutToFile(self, file):
        sys.stdout = open(file, "w", 0)
    
    def isPublic(self):
        return False
    
    def userHasFullAccess(self):
        return self.isPublic() or GalaxyInterface.userHasFullAccess(self.galaxy.getUserName())

    def userIsOneOfUs(self):
        return GalaxyInterface.userHasFullAccess(self.galaxy.getUserName())
    
    def _getAllGenomes(self):
        return [('----- Select -----', '', False)] + GalaxyInterface.getAllGenomes(self.galaxy.getUserName())
        
    def getGenomeElement(self):    
        return SelectElement('dbkey', self._getAllGenomes(), self.getGenome())

    def getGenome(self, id='dbkey'):
        if self.transaction.request.POST.has_key('dbkey'):
            return str(self.transaction.request.POST['dbkey'])
        elif self.transaction.request.POST.has_key(id):
            self.params['dbkey'] = str(self.transaction.request.POST[id])
            
        if self.params.has_key('dbkey'):
            return self.params.get('dbkey')
        elif self.params.has_key(id):
            self.params['dbkey'] = self.params.get(id)
        return self.params.get('dbkey', self._getAllGenomes()[0][1])

    def getDictOfAllGenomes(self):
        return OrderedDict([(x[0],False) for x in GalaxyInterface.getAllGenomes(self.galaxy.getUserName())])
        
    def getTrackElement(self, id, label, history=False, ucsc=False):
        datasets = []
        if history:
            try:
                datasets = self.galaxy.getHistory(GalaxyInterface.getSupportedGalaxyFileFormats())
            except Exception, e:
                print e
        element = TrackWrapper(id, GalaxyInterface, [], self.galaxy, datasets, self.getGenome(), ucscTracks=ucsc)
        element.fetchTracks()
        element.legend = label
        return element

    def getDataFilePath(self, id):
        if hasattr(self, 'galaxy'):
            return self.galaxy.getDataFilePath(id)
        if self.params.has_key('file_path'):
            return getDataFilePath(self.params['file_path'], id)
        return None

    def getHistoryTrackDef(self, input):
        if self.params.get(input) == 'galaxy':
            file = self.params.get(input + 'file')
            p = file.split(',')
            trkdef = ['galaxy', p[2], self.getDataFilePath(p[1]), unquote(p[3])]
            return trkdef
        return None

    def getTrackDef(self, input):
        trkdef = self.getHistoryTrackDef(input)
        if trkdef == None:
            trkdef = self.params.get(input).split(':')
        return trkdef

    def jsonCall(self, args):
        res = {}
        try:
            methodName = args['method']
            if methodName in self.jsonMethods:
                method = getattr(self, methodName)
                res = method(args)
        except Exception, e:
            res['exception'] = str(e)
        return res
