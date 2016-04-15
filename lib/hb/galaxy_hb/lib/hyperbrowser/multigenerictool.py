# Copyright (C) 2012, Geir Kjetil Sandve, Sveinung Gundersen, Kai Trengereid and Morten Johansen
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

import sys, os, json, pickle
from collections import namedtuple, OrderedDict, deque
from urllib import quote, unquote
from gold.application.GalaxyInterface import GalaxyInterface
from quick.webtools.GeneralGuiToolsFactory import GeneralGuiToolsFactory
from BaseToolController import BaseToolController
from generictool import GenericToolController

class MultiGenericToolController(GenericToolController):
    def __init__(self, trans, job):
        BaseToolController.__init__(self, trans, job)

        self.errorMessage = None
        self.toolId = self.params.get('tool_id', 'default_tool_id')

        if self.params.has_key('choices_stack'):
            self.choicesStack = pickle.loads(unquote(self.params.get('choices_stack')))
        else:
            self.choicesStack = deque()

        if self.params.has_key('old_values'):
            self.oldValues = json.loads(unquote(self.params.get('old_values')))
            self.use_default = False
        else:
            self.oldValues = {}
            self.use_default = True

        self.prototype = GeneralGuiToolsFactory.getWebTool(self.toolId)

        if self.params.has_key('next'):
            self.subClassId = self.prototype.getNextClass(self.choicesStack[-1])
        elif self.params.has_key('previous'):
            self.subClassId, self.initChoicesDict = self.choicesStack[-2]
        else:
            self.subClassId = unquote(self.params.get('sub_class_id', ''))


        self.subClasses = OrderedDict()
        subClasses = self.prototype.getSubToolClasses()
        if subClasses:
            #self.subClasses[self.prototype.getToolSelectionName()] = self.prototype
            for subcls in subClasses:
                self.subClasses[subcls.getToolSelectionName()] = subcls

        self.resetAll = False
        if self.subClassId and self.subClassId in self.subClasses:
            self.prototype = self.subClasses[self.subClassId]
            if not self.oldValues.has_key('sub_class_id') or self.oldValues['sub_class_id'] != self.subClassId:
                self.oldValues['sub_class_id'] = self.subClassId
                self.resetAll = True
        else:
            self.prototype = subClasses[0]

        self.inputTypes = []
        self.inputValues = []
        self.displayValues = []
        self.inputIds = []
        self.inputNames = []
        self.inputInfo = []
        self._getInputBoxNames()
        self.inputOrder = self._getIdxList(self.prototype.getInputBoxOrder())
        self.resetBoxes = self._getIdxList(self.prototype.getResetBoxes())

        self.trackElements = {}
        if trans:
            self.action()

            if self.params.has_key('next'):
                self.choicesStack.append((self.subClassId, self.choices._asdict()))
            elif self.params.has_key('previous'):
                self.choicesStack.pop()
            else:
                if len(self.choicesStack) > 0:
                    self.choicesStack[-1] = (self.subClassId, self.choices._asdict())
                else:
                    self.choicesStack.append((self.subClassId, self.choices._asdict()))

    def hasNextPage(self):
        return bool(self.prototype.getNextClass(self.choicesStack[-1]))

    def hasPrevPage(self):
        return len(self.choicesStack) > 1

    def execute(self):
        outputFormat = self.params['datatype'] if self.params.has_key('datatype') else 'html'
        if outputFormat in ['html','customhtml','hbfunction']:
            self.stdoutToHistory()

        print self.choicesStack


def getController(transaction = None, job = None):
    return MultiGenericToolController(transaction, job)
